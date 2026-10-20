# -*- coding: utf-8 -*-
"""
第一題：讀程式、追蹤變化（20 分）
本程式包含 1A、1B、1C、1D 之題目執行代碼、解析與標準答案輸出。
"""

def question_1a():
    print("=" * 50)
    print("【1A. 數值與型別】（6 分）")
    print("=" * 50)
    
    # 題目原始程式碼
    a = round(42.5)
    b = round(43.5)
    c = 7 / 2

    print("--- 實際執行輸出 ---")
    print(a)
    print(b)
    print(c)
    print(type(c))
    
    print("\n--- 逐步完成解答 ---")
    print("1. 寫出 a、b、c 的值：")
    print(f"   a = {a}")
    print(f"   b = {b}")
    print(f"   c = {c}")
    
    print("\n2. 寫出四行輸出的內容：")
    print(f"   第一行: {a}")
    print(f"   第二行: {b}")
    print(f"   第三行: {c}")
    print(f"   第四行: {type(c)}")
    
    print("\n3. 說明為什麼 a 與 b 的結果不同：")
    explanation = (
        "   說明：Python 內建的 round() 函式採用「銀行家捨入法」（round half to even，四捨六入五成雙）。\n"
        "   當小數部分剛好位於兩個整數正中間（例如 .5）時，會採用「取至最接近的偶數」規則：\n"
        "   - 42.5 位於整數 42 與 43 之間，最接近的偶數是 42，因此 round(42.5) 結果為 42。\n"
        "   - 43.5 位於整數 43 與 44 之間，最接近的偶數是 44，因此 round(43.5) 結果為 44。\n"
        "   兩者因為相鄰偶數不同，故結果不同。"
    )
    print(explanation)


def question_1b():
    print("\n" + "=" * 50)
    print("【1B. 追蹤遞迴呼叫】（6 分）")
    print("=" * 50)
    
    def gcd_trace(a, b, step=1, trace_table=None):
        if trace_table is not None:
            trace_table.append((step, a, b))
        if b == 0:
            return a
        return gcd_trace(b, a % b, step + 1, trace_table)
    
    trace_table = []
    result = gcd_trace(55, 21, 1, trace_table)
    
    print("1. gcd(55, 21) 每次呼叫的參數追蹤表：")
    print(f"{'呼叫順序':<10} {'a':<10} {'b':<10}")
    print("-" * 30)
    for step, a, b in trace_table:
        print(f"{step:<10} {a:<10} {b:<10}")
        
    print("\n2. 找出遞迴停止時符合的條件：")
    print("   遞迴停止條件為：b == 0（當第 8 次呼叫時，b 為 0，觸發停止條件）")
    
    print("\n3. 寫出最後回傳值：")
    print(f"   最後回傳值為：{result}")


def question_1c():
    print("\n" + "=" * 50)
    print("【1C. 串列別名】（4 分）")
    print("=" * 50)
    
    left = [2, 4]
    right = left
    right.append(6)
    left[0] = 10
    
    print("--- 實際執行輸出 ---")
    print(left)
    print(right)
    
    print("\n--- 逐步完成解答 ---")
    print("1. 寫出兩行輸出：")
    print(f"   第一行: {left}")
    print(f"   第二行: {right}")
    
    print("\n2. 用一句話說明 left 與 right 的關係：")
    explanation = (
        "   說明：left 與 right 變數皆指向記憶體中同一個串列物件（right 是 left 的別名/同參照），\n"
        "   因此透過任一名稱對該串列進行修改（如 append 或索引賦值），另一個名稱所見的串列內容也會同步改變。"
    )
    print(explanation)


def question_1d():
    print("\n" + "=" * 50)
    print("【1D. 字串索引與切片】（4 分）")
    print("=" * 50)
    
    word = "Python"
    print("--- 實際執行輸出 ---")
    print(word[0])
    print(word[1:4])
    print(len(word))
    
    print("\n--- 逐步完成解答 ---")
    print("1. 寫出三行輸出：")
    print(f"   第一行: {word[0]}")
    print(f"   第二行: {word[1:4]}")
    print(f"   第三行: {len(word)}")
    
    print("\n2. 指出切片的結尾索引是否包含在結果中：")
    explanation = (
        "   切片的結尾索引「不包含」在結果中。\n"
        "   Python 的切片語法 [start:end] 為「左閉右開」區間，即包含索引 start，但不包含索引 end。\n"
        "   因此 word[1:4] 只擷取索引 1、2、3 的字元（即 'y'、't'、'h'），不包含索引 4 的字元 'o'。"
    )
    print(explanation)


if __name__ == "__main__":
    question_1a()
    question_1b()
    question_1c()
    question_1d()
