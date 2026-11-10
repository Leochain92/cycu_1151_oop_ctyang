# Python 期中考規模練習題 - 完整解答報告

本目錄存放依據《Python 期中考規模練習題》題目要求所撰寫之 Python 程式解答。

---

## 檔案清單說明

| 檔名 | 對應題號 | 題目名稱 | 說明 |
| :--- | :--- | :--- | :--- |
| `q1_code_tracing.py` | 第一題 | 讀程式、追蹤變化 (20分) | 包含 1A (數值與型別)、1B (遞迴呼叫追蹤)、1C (串列別名)、1D (字串切片) 執行與詳細解答說明 |
| `q2_score_summary.py` | 第二題 | 成績清單摘要函式 (30分) | 實作 `print_score_summary(scores, passing_score)` 函式與測試範例 |
| `q3_palindrome.py` | 第三題 | 找出符合條件的長回文單字 (30分) | 實作 `is_palindrome(word)` 與 `find_long_palindromes(words, min_length)` |
| `q4_recursive_gcd.py` | 第四題 | 使用遞迴計算最大公因數 (20分) | 實作遞迴輾轉相除法函式 `gcd(a, b)` 與邊界測試 |
| `all_solutions.py` | 整合題解 | 整合執行檔 | 整合 1~4 題程式碼與測試，可一鍵執行全卷驗證 |

---

## 各題文字解答與解析

### 第一題：讀程式、追蹤變化（20 分）

#### 1A. 數值與型別（6 分）
1. **a、b、c 的值：**
   - `a = 42`
   - `b = 44`
   - `c = 3.5`
2. **四行輸出內容：**
   ```text
   42
   44
   3.5
   <class 'float'>
   ```
3. **為什麼 a 與 b 的結果不同：**
   Python 的 `round()` 函式採用「銀行家捨入法」（round half to even，取至最接近的偶數）。當小數剛好位於兩個整數正中間（.5）時，會採用「取至最接近的偶數」規則：
   - `42.5` 位於 42 與 43 中間，最接近的偶數是 **42**。
   - `43.5` 位於 43 與 44 中間，最接近的偶數是 **44**。
   因此兩者結果不同。

---

#### 1B. 追蹤遞迴呼叫（6 分）
1. **呼叫參數追蹤表：**

| 呼叫順序 | a | b |
| :---: | :---: | :---: |
| 1 | 55 | 21 |
| 2 | 21 | 13 |
| 3 | 13 | 8 |
| 4 | 8 | 5 |
| 5 | 5 | 3 |
| 6 | 3 | 2 |
| 7 | 2 | 1 |
| 8 | 1 | 0 |

2. **遞迴停止時符合的條件：**
   `b == 0`（第 8 次呼叫時符合此條件）。
3. **最後回傳值：**
   `1`

---

#### 1C. 串列別名（4 分）
1. **兩行輸出：**
   ```text
   [10, 4, 6]
   [10, 4, 6]
   ```
2. **left 與 right 的關係：**
   `left` 與 `right` 指向記憶體中同一個串列物件（`right` 為 `left` 的別名 / 參照同一個 list 實體），因此透過任一名稱修改串列（如 `append` 或透過索引改值），另一個變數所讀取到的內容也會同步改變。

---

#### 1D. 字串索引與切片（4 分）
1. **三行輸出：**
   ```text
   P
   yth
   6
   ```
2. **切片的結尾索引是否包含在結果中：**
   **不包含**。Python 的切片 `word[1:4]` 為左閉右開區間 `[start:stop)`，僅包含索引 1、2、3 的字元（即 `'y'`, `'t'`, `'h'`），結尾索引 4 的字元 `'o'` 不包含在結果內。

---

### 第二題：成績清單摘要函式（30 分）

- **函式宣告：** `print_score_summary(scores, passing_score)`
- **核心設計：**
  - 初始化總分與及格人數計數器。
  - 單次走訪串列累加總分，並同時判斷分數是否 `>= passing_score`。
  - 計算平均分數（`total / count`，不自行四捨五入）。
  - 以 f-string 印出指定標籤。
- **測試輸出：**
  ```text
  筆數：5
  總分：410
  平均：82.0
  及格人數：4
  ```

---

### 第三題：找出符合條件的長回文單字（30 分）

- **函式宣告：**
  - `is_palindrome(word)`：使用 `lower()` 正規化大小寫，以 `reversed()` 與 `''.join(...)` 反轉後進行比對，回傳 `True` 或 `False`。
  - `find_long_palindromes(words, min_length)`：篩選單字長度 `>= min_length` 且 `is_palindrome(word)` 為真者，依序保留原始拼寫回傳新串列。
- **測試結果：**
  - `is_palindrome("Noon")` $\rightarrow$ `True`
  - `is_palindrome("Python")` $\rightarrow$ `False`
  - `find_long_palindromes(words, 4)` $\rightarrow$ `['Noon', 'level', 'Radar', 'civic']`
  - `find_long_palindromes(words, 5)` $\rightarrow$ `['level', 'Radar', 'civic']`

---

### 第四題：使用遞迴計算最大公因數（20 分）

- **函式宣告：** `gcd(a, b)`
- **核心設計：**
  - 基底情況：`if b == 0: return a`
  - 遞迴步驟：`return gcd(b, a % b)`
- **測試結果：**
  - `gcd(55, 21)` $\rightarrow$ `1`
  - `gcd(24, 18)` $\rightarrow$ `6`
  - `gcd(7, 0)` $\rightarrow$ `7`
