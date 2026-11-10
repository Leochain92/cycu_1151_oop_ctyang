"""
全題整合執行 — 期中考練習題
姓名：連宥丞　學號：11472012
四題一次執行，供截圖使用。
"""

import csv
import html
import pathlib

# ============================================================
# 第一題：成績清單摘要函式
# ============================================================

def read_scores(filename):
    scores = []
    with open(filename, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores.append(float(row["學期成績"]))
    return scores

def print_score_summary(scores, passing_score):
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

# ============================================================
# 第二題：找出符合條件的長回文單字
# ============================================================

def is_palindrome(word):
    lower_word = word.lower()
    reversed_word = ''.join(reversed(lower_word))
    return lower_word == reversed_word

def find_long_palindromes(words, min_length):
    result = []
    for word in words:
        if len(word) >= min_length and is_palindrome(word):
            result.append(word)
    return result

# ============================================================
# 第三題：使用遞迴計算最大公因數
# ============================================================

def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

# ============================================================
# 第四題：電影評分資料分析
# ============================================================

def read_movies(filename):
    movies = []
    with open(filename, encoding="utf-8") as page:
        for line in page:
            if "<li data-rating=" in line:
                values = line.split('"')
                rating, votes, year = float(values[1]), int(values[3]), values[5]
                title = html.unescape(line.split(">", 1)[1].split("</li>", 1)[0])
                if rating >= 8.8 and votes >= 1_000_000:
                    movies.append((title, year, rating, votes))
    return movies

# ============================================================
# 整合執行
# ============================================================

SEP = "=" * 55

print(SEP)
print("  第一題：成績清單摘要函式")
print(SEP)
print("[ 小型測試 ] scores=[72,90,64,88,96], passing_score=70")
print_score_summary([72, 90, 64, 88, 96], 70)
print()
print("[ 等於門檻 ] scores=[50,60,70], passing_score=60")
print_score_summary([50, 60, 70], 60)
print()
base_dir = pathlib.Path(__file__).parent
print(f"[ 讀取 q1_oop_1132.csv ] passing_score=70")
scores_real = read_scores(base_dir / "q1_oop_1132.csv")
print_score_summary(scores_real, 70)

print()
print(SEP)
print("  第二題：找出符合條件的長回文單字")
print(SEP)
words = [
    "eye", "Eve", "mom", "Dad", "pop", "wow",
    "noon", "deed", "toot", "peep", "sees",
    "stats", "level", "Radar", "civic", "refer",
    "rotor", "kayak", "madam", "tenet", "solos", "minim",
    "redder", "racecar", "deified", "repaper",
    "rotator", "reviver", "redivider", "Malayalam",
]
print(f'is_palindrome("Noon")   = {is_palindrome("Noon")}')
print(f'is_palindrome("Python") = {is_palindrome("Python")}')
print()
r4 = find_long_palindromes(words, 4)
print(f"find_long_palindromes(words, 4) → 數量：{len(r4)}")
print(r4)
print()
r5 = find_long_palindromes(words, 5)
print(f"find_long_palindromes(words, 5) → 數量：{len(r5)}")
print(r5)

print()
print(SEP)
print("  第三題：遞迴最大公因數")
print(SEP)
print(f"gcd(55, 21)  = {gcd(55, 21)}")
print(f"gcd(24, 18)  = {gcd(24, 18)}")
print(f"gcd(7,  0)   = {gcd(7,  0)}")
print(f"gcd(101538353409718995449, 102328932531538938671)")
print(f"           = {gcd(101538353409718995449, 102328932531538938671)}")
print(f"gcd(105069657120960240421, 106722743827999341247)")
print(f"           = {gcd(105069657120960240421, 106722743827999341247)}")
print(f"gcd(108783078564548485001, 109275155618878610479)")
print(f"           = {gcd(108783078564548485001, 109275155618878610479)}")

print()
print(SEP)
print("  第四題：電影評分資料分析")
print(SEP)
html_path = base_dir / "q4_sample_page" / "q4_sample_page.html"
movies = read_movies(html_path)
for title, year, rating, votes in movies:
    print(f"{title} ({year}) - {rating} ({votes:,} votes)")
print("符合電影數量：", len(movies))

print()
print(SEP)
print("  全題執行完畢")
print(SEP)
