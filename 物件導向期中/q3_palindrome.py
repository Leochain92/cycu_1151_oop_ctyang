# -*- coding: utf-8 -*-
"""
第三題：找出符合條件的長回文單字（30 分）

題目要求：
回文是正讀與反讀相同的字串。本題資料只含英文字母；判斷時忽略大小寫，不需處理標點符號。

逐步引導：
1. 在 is_palindrome 中，先用 lower() 建立不分大小寫的字串。
2. 以 reversed() 與 ''.join(...) 建立反轉字串。
3. 比較轉成小寫的字串與反轉後的字串；相同時回傳 True，否則回傳 False。
4. 在 find_long_palindromes 中建立空串列，逐項走訪輸入的 words。
5. 只有在「長度至少為 min_length」且「是回文」時，才把原本拼寫的單字加進結果串列。
6. 走訪結束後回傳結果串列；不要在函式中直接印出結果。
"""

def is_palindrome(word):
    """
    判斷單字是否為回文（忽略大小寫）。
    
    參數:
        word (str): 要檢查的單字字串
    回傳:
        bool: 若為回文回傳 True，否則回傳 False
    """
    # 步驟 1: 先用 lower() 建立不分大小寫的字串
    lower_word = word.lower()
    
    # 步驟 2: 以 reversed() 與 ''.join(...) 建立反轉字串
    reversed_word = ''.join(reversed(lower_word))
    
    # 步驟 3: 比較轉成小寫的字串與反轉後的字串；相同時回傳 True，否則回傳 False
    return lower_word == reversed_word


def find_long_palindromes(words, min_length):
    """
    找出串列中長度至少為 min_length 的所有回文單字，維持原始順序與拼寫。
    
    參數:
        words (list): 單字字串串列
        min_length (int): 最小字元長度門檻
    回傳:
        list: 符合條件的單字串列
    """
    # 步驟 4: 在 find_long_palindromes 中建立空串列
    result = []
    
    # 逐項走訪輸入的 words
    for word in words:
        # 步驟 5: 只有在「長度至少為 min_length」且「是回文」時，才把原本拼寫的單字加進結果串列
        if len(word) >= min_length and is_palindrome(word):
            result.append(word)
            
    # 步驟 6: 走訪結束後回傳結果串列；不要在函式中直接印出結果
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("【is_palindrome 單元測試】")
    print("=" * 50)
    test1 = is_palindrome("Noon")
    test2 = is_palindrome("Python")
    print(f'is_palindrome("Noon") -> {test1} (預期: True)')
    print(f'is_palindrome("Python") -> {test2} (預期: False)')
    
    # 額外自我測試
    print(f'is_palindrome("Racecar") -> {is_palindrome("Racecar")} (預期: True)')
    print(f'is_palindrome("Madam") -> {is_palindrome("Madam")} (預期: True)')
    print(f'is_palindrome("algorithm") -> {is_palindrome("algorithm")} (預期: False)')
    
    print("\n" + "=" * 50)
    print("【find_long_palindromes 測試】")
    print("=" * 50)
    words = ["Noon", "level", "Python", "Radar", "civic", "data"]
    print(f"原始單字清單: {words}\n")
    
    # 測試 1: min_length = 4
    res_len4 = find_long_palindromes(words, 4)
    print(f"find_long_palindromes(words, 4) 結果:")
    print(f"-> {res_len4}")
    print(f"符合個數: {len(res_len4)} 個 (依序保留原始拼寫)")
    
    # 測試 2: min_length = 5
    res_len5 = find_long_palindromes(words, 5)
    print(f"\nfind_long_palindromes(words, 5) 結果:")
    print(f"-> {res_len5}")
    print(f"符合個數: {len(res_len5)} 個")
    
    # 測試 3: 自我測試 min_length = 6
    res_len6 = find_long_palindromes(words, 6)
    print(f"\nfind_long_palindromes(words, 6) 自我測試結果:")
    print(f"-> {res_len6}")
