from __future__ import annotations

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # 修正 Anaconda + PyTorch OMP 衝突

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


COCO_CLASS_NAME_TO_ID = {
	"bicycle": 1,
	"car": 2,
	"motorcycle": 3,
	"bus": 5,
	"truck": 7,
}


@dataclass
class CrossingEvent:
	frame_index: int
	timestamp_sec: float
	track_id: int
	class_id: int
	class_name: str
	confidence: float
	direction: str
	line_x1: int
	line_y1: int
	line_x2: int
	line_y2: int


def eprint(msg: str) -> None:
	print(msg, file=sys.stderr, flush=True)


def parse_line_arg(raw: str) -> tuple[tuple[int, int], tuple[int, int]]:
	parts = [p.strip() for p in raw.split(",")]
	if len(parts) != 4:
		raise ValueError("line must be in format x1,y1,x2,y2")
	x1, y1, x2, y2 = map(int, parts)
	return (x1, y1), (x2, y2)


def parse_vehicle_classes(raw: str) -> list[int]:
	requested = [p.strip().lower() for p in raw.split(",") if p.strip()]
	if not requested:
		raise ValueError("vehicle classes cannot be empty")

	class_ids: list[int] = []
	invalid: list[str] = []
	aliases = {
		"motorbike": "motorcycle",
		"scooter": "motorcycle",
		"bike": "motorcycle",
		"lorry": "truck",
		"heavy_truck": "truck",
	}
	for name in requested:
		canonical = aliases.get(name, name)
		class_id = COCO_CLASS_NAME_TO_ID.get(canonical)
		if class_id is None:
			invalid.append(name)
			continue
		class_ids.append(class_id)

	if invalid:
		supported = ", ".join(sorted(COCO_CLASS_NAME_TO_ID.keys()))
		raise ValueError(
			f"unsupported class names: {', '.join(invalid)}. Supported: {supported}"
		)

	return sorted(set(class_ids))


def side_of_line(
	point: tuple[float, float], a: tuple[int, int], b: tuple[int, int]
) -> float:
	px, py = point
	ax, ay = a
	bx, by = b
	return (bx - ax) * (py - ay) - (by - ay) * (px - ax)


def detect_direction(prev_side: float, curr_side: float) -> str:
	if prev_side < 0 <= curr_side:
		return "A_to_B"
	if prev_side > 0 >= curr_side:
		return "B_to_A"
	return "unknown"


def select_line_interactively(frame: np.ndarray) -> tuple[tuple[int, int], tuple[int, int]]:
	points: list[tuple[int, int]] = []
	window_name = "Select counting line: click 2 points, Enter confirm, R reset, ESC cancel"
	display = frame.copy()

	def redraw() -> None:
		nonlocal display
		display = frame.copy()
		if len(points) >= 1:
			cv2.circle(display, points[0], 6, (0, 255, 255), -1)
		if len(points) == 2:
			cv2.circle(display, points[1], 6, (0, 255, 255), -1)
			cv2.line(display, points[0], points[1], (0, 255, 255), 2)

	def on_mouse(event: int, x: int, y: int, flags: int, param: object) -> None:
		del flags, param
		if event != cv2.EVENT_LBUTTONDOWN:
			return
		if len(points) < 2:
			points.append((x, y))
		else:
			points[1] = (x, y)
		redraw()

	cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
	cv2.setMouseCallback(window_name, on_mouse)

	while True:
		cv2.imshow(window_name, display)
		key = cv2.waitKey(20) & 0xFF
		if key in (13, 10):  # Enter
			if len(points) == 2:
				cv2.destroyWindow(window_name)
				return points[0], points[1]
			eprint("Please click 2 points before confirming.")
		elif key in (27,):  # ESC
			cv2.destroyWindow(window_name)
			raise RuntimeError("Line selection cancelled by user.")
		elif key in (ord("r"), ord("R")):
			points.clear()
			redraw()


def create_writer_with_fallback(
	out_path: Path, fps: float, width: int, height: int
) -> tuple[cv2.VideoWriter, str]:
	codecs = ["avc1", "mp4v"]
	for codec in codecs:
		fourcc = cv2.VideoWriter_fourcc(*codec)
		writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))
		if writer.isOpened():
			return writer, codec
		writer.release()
	raise RuntimeError(
		"Unable to open output video writer. Tried codecs: " + ", ".join(codecs)
	)


def write_events_csv(out_csv: Path, events: list[CrossingEvent]) -> None:
	fieldnames = [
		"frame_index",
		"timestamp_sec",
		"track_id",
		"class_id",
		"class_name",
		"confidence",
		"direction",
		"line_x1",
		"line_y1",
		"line_x2",
		"line_y2",
	]
	with out_csv.open("w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for event in events:
			writer.writerow(
				{
					"frame_index": event.frame_index,
					"timestamp_sec": f"{event.timestamp_sec:.3f}",
					"track_id": event.track_id,
					"class_id": event.class_id,
					"class_name": event.class_name,
					"confidence": f"{event.confidence:.4f}",
					"direction": event.direction,
					"line_x1": event.line_x1,
					"line_y1": event.line_y1,
					"line_x2": event.line_x2,
					"line_y2": event.line_y2,
				}
			)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Count vehicles crossing a user-defined line with YOLO tracking."
	)
	parser.add_argument(
		"--video",
		type=Path,
		default=Path(r"C:\Users\user\Documents\GitHub\cycu_1151_oop_ctyang\交通資料範本\vedio-sample-4AM\yolo_cars\HSZ169_20261117_143751.mp4"),
		help="Input video path",
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=None,
		help="Output directory for CSV and annotated MOV. Default: video directory.",
	)
	parser.add_argument(
		"--model",
		type=str,
		default="yolov8n.pt",
		help="YOLO model name or local model path",
	)
	parser.add_argument(
		"--confidence",
		type=float,
		default=0.35,
		help="General detection confidence threshold (cars/trucks/buses)",
	)
	parser.add_argument(
		"--moto-confidence",
		type=float,
		default=0.20,
		help="Special sensitive confidence threshold for motorcycles (default: 0.20)",
	)
	parser.add_argument(
		"--imgsz",
		type=int,
		default=960,
		help="YOLO inference image size (e.g. 640, 960, 1280). Larger size improves small motorcycle detection.",
	)
	parser.add_argument(
		"--merge-bicycle",
		action="store_true",
		default=True,
		help="Merge 'bicycle' detections into 'motorcycle' (Taiwan scooters are often misclassified as bicycle).",
	)
	parser.add_argument(
		"--iou",
		type=float,
		default=0.45,
		help="NMS IoU threshold",
	)
	parser.add_argument(
		"--vehicle-classes",
		type=str,
		default="car,motorcycle,truck,bus,bicycle",
		help="Comma-separated classes from: car,motorcycle,bus,truck,bicycle",
	)
	parser.add_argument(
		"--line",
		type=str,
		default="",
		help="Optional pre-defined line in x1,y1,x2,y2. If omitted, interactive selection is used.",
	)
	parser.add_argument(
		"--show",
		action="store_true",
		help="Show live preview while processing",
	)
	parser.add_argument(
		"--cooldown-frames",
		type=int,
		default=8,
		help="Minimum frames between crossings for same track ID",
	)
	parser.add_argument(
		"--max-frames",
		type=int,
		default=-1,
		help="Process at most N frames (-1 means 2 minutes, 0 means full video)",
	)
	return parser


def main() -> int:
	args = build_parser().parse_args()

	input_video = args.video.expanduser().resolve()
	if not input_video.exists():
		eprint(f"Input video not found: {input_video}")
		return 1

	output_dir = (
		args.output_dir.expanduser().resolve() if args.output_dir else input_video.parent
	)
	output_dir.mkdir(parents=True, exist_ok=True)

	try:
		class_ids = parse_vehicle_classes(args.vehicle_classes)
	except ValueError as err:
		eprint(str(err))
		return 1

	cap = cv2.VideoCapture(str(input_video))
	if not cap.isOpened():
		eprint(f"Unable to open video: {input_video}")
		return 1

	fps = float(cap.get(cv2.CAP_PROP_FPS))
	if fps <= 0:
		fps = 30.0
	if args.max_frames < 0:
		args.max_frames = int(round(fps * 120))
		eprint(f"Auto max-frames (2 minutes): {args.max_frames}")
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

	ok, first_frame = cap.read()
	if not ok or first_frame is None:
		cap.release()
		eprint("Unable to read first frame from input video.")
		return 1

	try:
		line_a, line_b = (
			parse_line_arg(args.line) if args.line else select_line_interactively(first_frame)
		)
	except (ValueError, RuntimeError) as err:
		cap.release()
		eprint(str(err))
		return 1

	stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_name = input_video.stem
	out_video = output_dir / f"{base_name}_counted_{stamp}.mov"
	out_csv = output_dir / f"{base_name}_crossings_{stamp}.csv"

	try:
		writer, codec = create_writer_with_fallback(out_video, fps, width, height)
	except RuntimeError as err:
		cap.release()
		eprint(str(err))
		return 1

	eprint(f"Output video codec: {codec}")
	eprint(f"Loading YOLO model: {args.model}")
	model = YOLO(args.model)
	selected_class_names = [model.names.get(class_id, str(class_id)) for class_id in class_ids]
	if args.merge_bicycle and "bicycle" in selected_class_names:
		selected_class_names = [name for name in selected_class_names if name != "bicycle"]
		if "motorcycle" not in selected_class_names:
			selected_class_names.append("motorcycle")
	class_cross_counts: dict[str, int] = {name: 0 for name in selected_class_names}

	track_last_side: dict[int, float] = {}
	track_last_cross_frame: dict[int, int] = {}
	crossings: list[CrossingEvent] = []
	total_crossings = 0
	recent_text = ""

	frame_index = 0
	cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

	while True:
		if args.max_frames > 0 and frame_index >= args.max_frames:
			eprint(f"Reached max frames limit: {args.max_frames}")
			break

		ok, frame = cap.read()
		if not ok:
			break

		track_conf = min(args.confidence, args.moto_confidence)
		results = model.track(
			frame,
			persist=True,
			tracker="bytetrack.yaml",
			verbose=False,
			conf=track_conf,
			iou=args.iou,
			imgsz=args.imgsz,
			classes=class_ids,
		)

		annotated = frame.copy()
		cv2.line(annotated, line_a, line_b, (0, 255, 255), 3)

		if results and results[0].boxes is not None:
			boxes = results[0].boxes
			ids = boxes.id.int().cpu().tolist() if boxes.id is not None else []
			cls = boxes.cls.int().cpu().tolist() if boxes.cls is not None else []
			confs = boxes.conf.cpu().tolist() if boxes.conf is not None else []
			xyxy = boxes.xyxy.cpu().tolist() if boxes.xyxy is not None else []

			n = min(len(ids), len(cls), len(confs), len(xyxy))
			for i in range(n):
				track_id = int(ids[i])
				class_id = int(cls[i])
				class_name = model.names.get(class_id, str(class_id))
				confidence = float(confs[i])

				# 台灣速克達容易被 COCO 模型判定為 bicycle，依設定自動合併為 motorcycle
				if args.merge_bicycle and class_name == "bicycle":
					class_name = "motorcycle"

				# 根據類別採用不同的敏感度門檻（機車預設採用較靈敏的 0.20）
				req_conf = args.moto_confidence if class_name in ("motorcycle", "bicycle") else args.confidence
				if confidence < req_conf:
					continue
				x1, y1, x2, y2 = [int(v) for v in xyxy[i]]
				cx = (x1 + x2) / 2.0
				cy = (y1 + y2) / 2.0

				curr_side = side_of_line((cx, cy), line_a, line_b)
				prev_side = track_last_side.get(track_id)

				if prev_side is not None and prev_side * curr_side < 0:
					last_cross_frame = track_last_cross_frame.get(track_id, -10**9)
					if frame_index - last_cross_frame >= args.cooldown_frames:
						total_crossings += 1
						class_cross_counts[class_name] = class_cross_counts.get(class_name, 0) + 1
						direction = detect_direction(prev_side, curr_side)
						evt = CrossingEvent(
							frame_index=frame_index,
							timestamp_sec=frame_index / fps,
							track_id=track_id,
							class_id=class_id,
							class_name=class_name,
							confidence=confidence,
							direction=direction,
							line_x1=line_a[0],
							line_y1=line_a[1],
							line_x2=line_b[0],
							line_y2=line_b[1],
						)
						crossings.append(evt)
						track_last_cross_frame[track_id] = frame_index
						recent_text = (
							f"Crossed: id={track_id} {class_name} {direction} total={total_crossings}"
						)

				track_last_side[track_id] = curr_side

				color = (60, 200, 255)
				cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
				cv2.circle(annotated, (int(cx), int(cy)), 3, color, -1)
				cv2.putText(
					annotated,
					f"ID {track_id} {class_name} {confidence:.2f}",
					(x1, max(20, y1 - 8)),
					cv2.FONT_HERSHEY_SIMPLEX,
					0.55,
					color,
					2,
					cv2.LINE_AA,
				)

		cv2.putText(
			annotated,
			f"Total crossings: {total_crossings}",
			(20, 40),
			cv2.FONT_HERSHEY_SIMPLEX,
			1.0,
			(0, 255, 0),
			2,
			cv2.LINE_AA,
		)
		if recent_text:
			cv2.putText(
				annotated,
				recent_text,
				(20, 75),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.7,
				(255, 255, 255),
				2,
				cv2.LINE_AA,
			)

		line_summary = " | ".join(
			f"{name}: {class_cross_counts.get(name, 0)}" for name in selected_class_names
		)
		line_mid_x = (line_a[0] + line_b[0]) // 2
		line_mid_y = (line_a[1] + line_b[1]) // 2
		(summary_w, summary_h), _ = cv2.getTextSize(
			line_summary,
			cv2.FONT_HERSHEY_SIMPLEX,
			0.65,
			2,
		)
		text_x = max(10, min(width - summary_w - 20, line_mid_x - summary_w // 2))
		text_y = max(summary_h + 10, min(height - 10, line_mid_y - 12))
		cv2.rectangle(
			annotated,
			(text_x - 6, text_y - summary_h - 8),
			(text_x + summary_w + 6, text_y + 6),
			(0, 0, 0),
			-1,
		)
		cv2.putText(
			annotated,
			line_summary,
			(text_x, text_y),
			cv2.FONT_HERSHEY_SIMPLEX,
			0.65,
			(0, 255, 255),
			2,
			cv2.LINE_AA,
		)

		writer.write(annotated)

		if args.show:
			cv2.imshow("Vehicle crossing counter", annotated)
			key = cv2.waitKey(1) & 0xFF
			if key in (27, ord("q"), ord("Q")):
				eprint("Stopped early by user.")
				break

		frame_index += 1

	cap.release()
	writer.release()
	cv2.destroyAllWindows()

	write_events_csv(out_csv, crossings)

	eprint(f"Done. Total crossings: {total_crossings}")
	eprint(f"CSV: {out_csv}")
	eprint(f"Annotated video: {out_video}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
