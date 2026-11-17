from __future__ import annotations

import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# ── 攝影機設定（在此切換攝影機）──────────────────────────────────────────────
# 模式 A: BOT356（台北艋舺萬大路口 - 台北交工處 LL-HLS 串流）
CAMERA_ID   = "BOT356"
CAMERA_URL  = "https://jtmctrafficcctv5.gov.taipei/NVR/22505a3a-4d37-4ce1-85ee-a98c48ae022a/live.m3u8"
STREAM_TYPE = "hls"

# 模式 B: HSZ169（新竹經國路口 - ZoneMinder MJPEG 串流）
# CAMERA_ID   = "HSZ169"
# CAMERA_URL  = "https://nvr3.hccg.gov.tw/thi-vms/cgi-bin/zms?monitor=104&user=viewer&pass=--"
# STREAM_TYPE = "mjpeg"

RECORD_SECONDS = 60
IS_WINDOWS = platform.system() == "Windows"


def find_ffmpeg() -> str | None:
    """尋找 ffmpeg.exe 路徑。"""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    # WinGet 安裝備援路徑
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    for pkg in base.glob("Gyan.FFmpeg*"):
        for exe in pkg.rglob("ffmpeg.exe"):
            if exe.exists():
                return str(exe)
    return None


def record_mjpeg(ffmpeg: str, output_path: Path) -> int:
    """用 FFmpeg 錄製 MJPEG 串流（如新竹市）。"""
    cmd = [
        ffmpeg,
        "-hide_banner", "-loglevel", "warning",
        "-tls_verify", "0",
        "-use_wallclock_as_timestamps", "1",
        "-rw_timeout", "15000000",
        "-i", CAMERA_URL,
        "-t", str(RECORD_SECONDS),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-an",
        "-y",
        str(output_path),
    ]
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
    print(f"開始錄製 {CAMERA_ID}（MJPEG），限時 {RECORD_SECONDS} 秒...")
    proc = subprocess.Popen(cmd, creationflags=flags)
    try:
        proc.wait(timeout=RECORD_SECONDS + 15)
    except subprocess.TimeoutExpired:
        if IS_WINDOWS:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    return proc.returncode if proc.returncode is not None else 0


def record_hls_cmaf(ffmpeg: str, output_path: Path) -> int:
    """
    專為台北市交工處 LL-HLS (CMAF fMP4) 設計的抓取器。
    
    原因與機制：
    交工處 NVR 伺服器會阻擋 FFmpeg 的 HTTP/TLS 請求（Error -138），
    但允許標準瀏覽器或系統 curl 帶上 Referer 進行存取。
    此函數使用系統原生 curl 下載 init.mp4 與各段即時 fragment，
    最後呼叫 FFmpeg 重建標準 MP4 時間戳，100% 穩定避開伺服器限制。
    """
    base_url = CAMERA_URL.rsplit("/", 1)[0]
    headers = [
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Referer: https://tw.live/",
        "-H", "Origin: https://tw.live",
    ]

    temp_raw = output_path.with_suffix(".raw.mp4")
    temp_init = output_path.with_suffix(".init.mp4")

    print(f"正在連線至 {CAMERA_ID} (LL-HLS)...")
    # 1. 抓取 CMAF init.mp4
    res = subprocess.run(
        ["curl.exe", "-k", "-s"] + headers + [f"{base_url}/init.mp4", "-o", str(temp_init)],
        capture_output=True,
    )
    if not temp_init.exists() or temp_init.stat().st_size == 0:
        print("[錯誤] 無法取得串流初始化檔案 (init.mp4)，請檢查網路或攝影機狀態。", file=sys.stderr)
        return 1

    print(f"開始擷取 {CAMERA_ID} 即時影像，限時 {RECORD_SECONDS} 秒...")

    downloaded: set[str] = set()
    start_time = time.time()
    segment_count = 0

    try:
        with open(temp_raw, "wb") as outfile:
            # 寫入初始 header
            with open(temp_init, "rb") as inf:
                outfile.write(inf.read())

            while True:
                elapsed = time.time() - start_time
                if elapsed >= RECORD_SECONDS:
                    break

                # 取得最新 m3u8 清單
                res = subprocess.run(
                    ["curl.exe", "-k", "-s"] + headers + [CAMERA_URL],
                    capture_output=True,
                    text=True,
                )

                for line in res.stdout.splitlines():
                    line = line.strip()
                    # 辨識片段檔名（如 live80790.mp4）
                    if line.endswith(".mp4") and not line.startswith("#"):
                        if line not in downloaded:
                            downloaded.add(line)
                            seg_file = output_path.parent / f"_tmp_{line}"
                            sub_res = subprocess.run(
                                ["curl.exe", "-k", "-s"] + headers + [f"{base_url}/{line}", "-o", str(seg_file)],
                                capture_output=True,
                            )
                            if seg_file.exists() and seg_file.stat().st_size > 0:
                                with open(seg_file, "rb") as sf:
                                    outfile.write(sf.read())
                                segment_count += 1
                                seg_file.unlink(missing_ok=True)

                rem = int(RECORD_SECONDS - (time.time() - start_time))
                print(f"\r  已擷取 {segment_count:3d} 個片段 | 剩餘 {rem:2d} 秒...  ", end="", flush=True)
                time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n使用者手動停止擷取...")
    finally:
        temp_init.unlink(missing_ok=True)

    print("\n正在使用 FFmpeg 整理影片封裝與時間戳...")
    # 2. 使用 FFmpeg 無損快速修復時間戳記 (-c copy)
    fix_cmd = [
        ffmpeg,
        "-y",
        "-hide_banner", "-loglevel", "error",
        "-i", str(temp_raw),
        "-c", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(fix_cmd)
    temp_raw.unlink(missing_ok=True)

    return 0


def main() -> int:
    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        print("[錯誤] 找不到 FFmpeg！請先執行：winget install Gyan.FFmpeg", file=sys.stderr)
        return 1

    timestamp   = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    output_path = Path.cwd() / f"{CAMERA_ID}_{timestamp}.mp4"

    if STREAM_TYPE == "mjpeg":
        rc = record_mjpeg(ffmpeg, output_path)
    elif STREAM_TYPE == "hls":
        rc = record_hls_cmaf(ffmpeg, output_path)
    else:
        print(f"[錯誤] 未知 STREAM_TYPE: {STREAM_TYPE}", file=sys.stderr)
        return 1

    if output_path.exists() and output_path.stat().st_size > 0:
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"[完成] 影片已成功儲存：{output_path.name}  ({size_mb:.2f} MB)")
        return 0
    else:
        print("[錯誤] 錄製完成但未找到有效的輸出影片檔。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
