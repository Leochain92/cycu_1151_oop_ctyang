"""
第一題：成績清單摘要函式（30 分）
使用 csv.DictReader 讀取 q1_oop_1132.csv 中的「學期成績」欄，
計算並印出筆數、總分、平均與及格人數。
"""

import csv
from pathlib import Path


def read_scores(filename):
    """
    讀取 CSV 檔案，將「學期成績」欄位的成績轉為數值並放入 scores 串列後回傳。

    Args:
        filename: CSV 檔案路徑（字串）

    Returns:
        list: 包含每筆學期成績（float）的串列
    """
    scores = []
    file_path = Path(filename)
    if not file_path.is_absolute():
        file_path = Path(__file__).resolve().parent / filename

    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores.append(float(row["學期成績"]))
    return scores


def print_score_summary(scores, passing_score):
    """
    接收成績串列與及格門檻，依序印出：筆數、總分、平均與及格人數。

    Args:
        scores: 成績串列（list of float）
        passing_score: 及格門檻（數值），大於或等於門檻皆算及格
    """
    total = 0
    passing_count = 0
    for score in scores:
        total += score
        if score >= passing_score:
            passing_count += 1
    count = len(scores)
    average = total / count
    print(f"筆數：{count}")
    print(f"總分：{total}")
    print(f"平均：{average}")
    print(f"及格人數：{passing_count}")


# ===== 測試 =====
print("--- 小型測試資料 ---")
scores_test = [72, 90, 64, 88, 96]
print_score_summary(scores_test, 70)

print()
print("--- 等於門檻測試 ---")
print_score_summary([50, 60, 70], 60)

print()
print("--- 讀取 q1_oop_1132.csv，passing_score=70 ---")
scores_real = read_scores("q1_oop_1132.csv")
print_score_summary(scores_real, 70)
