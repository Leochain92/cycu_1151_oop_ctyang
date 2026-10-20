# -*- coding: utf-8 -*-
"""
Python 期中考規模練習題 - 完整整合解答
包含第一題到第四題所有題目實作與自動驗證。
"""

# ==========================================
# 第一題：讀程式、追蹤變化（20 分）
# ==========================================
def run_question_1():
    print("=" * 60)
    print("【第一題：讀程式、追蹤變化】（20 分）")
    print("=" * 60)
    
    # 1A
    print("\n--- 1A. 數值與型別 (6 分) ---")
    a = round(42.5)
    b = round(43.5)
    c = 7 / 2
    print(f"輸出行 1 (a): {a}")
    print(f"輸出行 2 (b): {b}")
    print(f"輸出行 3 (c): {c}")
    print(f"輸出行 4 (type(c)): {type(c)}")
    print("【說明】：Python round() 採用取至最接近偶數規則（round half to even），")
    print("42.5 靠近偶數 42，43.5 靠近偶數 44，因此兩者結果不同。")
    
    # 1B
    print("\n--- 1B. 追蹤遞迴呼叫 (6 分) ---")
    def gcd_track(a, b, step=1, records=None):
        if records is not None:
            records.append((step, a, b))
        if b == 0:
            return a
        return gcd_track(b, a % b, step + 1, records)
        
    records = []
    res_gcd = gcd_track(55, 21, 1, records)
    print(f"{'呼叫順序':<10} {'a':<10} {'b':<10}")
    print("-" * 30)
    for s, x, y in records:
        print(f"{s:<10} {x:<10} {y:<10}")
    print("遞迴停止條件：b == 0")
    print(f"最後回傳值：{res_gcd}")
    
    # 1C
    print("\n--- 1C. 串列別名 (4 分) ---")
    left = [2, 4]
    right = left
    right.append(6)
    left[0] = 10
    print(f"left:  {left}")
    print(f"right: {right}")
    print("【關係說明】：left 與 right 指向記憶體中同一個串列物件，修改其一會反映在另一變數上。")
    
    # 1D
    print("\n--- 1D. 字串索引與切片 (4 分) ---")
    word = "Python"
    print(f"word[0]:    {word[0]}")
    print(f"word[1:4]:  {word[1:4]}")
    print(f"len(word):  {len(word)}")
    print("【切片結尾索引說明】：不包含在結果中，Python 切片是左閉右開 [start:stop)。")


# ==========================================
# 第二題：成績清單摘要函式（30 分）
# ==========================================
def print_score_summary(scores, passing_score):
    """
    接收整數串列 scores 與及格門檻 passing_score，印出四行摘要：
    筆數、總分、平均、及格人數。
    """
    total_score = 0
    passing_count = 0
    for score in scores:
        total_score += score
        if score >= passing_score:
            passing_count += 1
            
    count = len(scores)
    average = total_score / count
    
    print(f"筆數：{count}")
    print(f"總分：{total_score}")
    print(f"平均：{average}")
    print(f"及格人數：{passing_count}")


def run_question_2():
    print("\n" + "=" * 60)
    print("【第二題：成績清單摘要函式】（30 分）")
    print("=" * 60)
    scores = [72, 90, 64, 88, 96]
    print("[測試資料 1: scores=[72, 90, 64, 88, 96], passing_score=70]")
    print_score_summary(scores, 70)
    
    print("\n[測試資料 2: scores=[50, 60, 70], passing_score=60]")
    print_score_summary([50, 60, 70], 60)


# ==========================================
# 第三題：找出符合條件的長回文單字（30 分）
# ==========================================
def is_palindrome(word):
    """判斷單字是否為回文（忽略大小寫，使用 lower, reversed, join）"""
    lower_word = word.lower()
    reversed_word = ''.join(reversed(lower_word))
    return lower_word == reversed_word

def find_long_palindromes(words, min_length):
    """回傳長度 >= min_length 且為回文的單字串列（維持原拼寫與順序）"""
    result = []
    for word in words:
        if len(word) >= min_length and is_palindrome(word):
            result.append(word)
    return result

def run_question_3():
    print("\n" + "=" * 60)
    print("【第三題：找出符合條件的長回文單字】（30 分）")
    print("=" * 60)
    print(f'is_palindrome("Noon"):   {is_palindrome("Noon")} (預期: True)')
    print(f'is_palindrome("Python"): {is_palindrome("Python")} (預期: False)')
    
    words = ["Noon", "level", "Python", "Radar", "civic", "data"]
    print(f"\n單字庫: {words}")
    res4 = find_long_palindromes(words, 4)
    print(f"find_long_palindromes(words, 4): {res4}")
    res5 = find_long_palindromes(words, 5)
    print(f"find_long_palindromes(words, 5): {res5}")


# ==========================================
# 第四題：使用遞迴計算最大公因數（20 分）
# ==========================================
def gcd(a, b):
    """以遞迴輾轉相除法計算最大公因數（不使用 math.gcd）"""
    if b == 0:
        return a
    return gcd(b, a % b)

def run_question_4():
    print("\n" + "=" * 60)
    print("【第四題：使用遞迴計算最大公因數】（20 分）")
    print("=" * 60)
    tests = [(55, 21), (24, 18), (7, 0)]
    for a, b in tests:
        print(f"gcd({a}, {b}) = {gcd(a, b)}")


if __name__ == "__main__":
    run_question_1()
    run_question_2()
    run_question_3()
    run_question_4()
