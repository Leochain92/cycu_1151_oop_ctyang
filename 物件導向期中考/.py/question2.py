"""
第二題：找出符合條件的長回文單字（30 分）
回文：正讀與反讀相同；判斷時忽略大小寫，結果保留原始拼寫及順序。
"""


def is_palindrome(word):
    """
    判斷 word 是否為回文（忽略大小寫）。

    Args:
        word: 要判斷的單字（字串）

    Returns:
        bool: 是回文回傳 True，否則回傳 False
    """
    lower_word = word.lower()
    reversed_word = ''.join(reversed(lower_word))
    return lower_word == reversed_word


def find_long_palindromes(words, min_length):
    """
    從 words 中篩選長度至少為 min_length 且為回文的單字。

    Args:
        words: 單字串列（list of str）
        min_length: 最小長度門檻（int）

    Returns:
        list: 符合條件的單字串列（保留原始拼寫及順序）
    """
    result = []
    for word in words:
        if len(word) >= min_length and is_palindrome(word):
            result.append(word)
    return result


# ===== 題目提供的測試資料 =====
words = [
    "eye", "Eve", "mom", "Dad", "pop", "wow",
    "noon", "deed", "toot", "peep", "sees",
    "stats", "level", "Radar", "civic", "refer",
    "rotor", "kayak", "madam", "tenet", "solos", "minim",
    "redder", "racecar", "deified", "repaper",
    "rotator", "reviver", "redivider", "Malayalam",
]

# ===== 測試 is_palindrome =====
print("--- is_palindrome 測試 ---")
print(f'is_palindrome("Noon") = {is_palindrome("Noon")}')    # True
print(f'is_palindrome("Python") = {is_palindrome("Python")}')  # False

# ===== 測試 find_long_palindromes =====
print()
print("--- find_long_palindromes(words, 4)（應有 24 個）---")
result_4 = find_long_palindromes(words, 4)
print(result_4)
print(f"數量：{len(result_4)}")

print()
print("--- find_long_palindromes(words, 5)（應有 19 個）---")
result_5 = find_long_palindromes(words, 5)
print(result_5)
print(f"數量：{len(result_5)}")
