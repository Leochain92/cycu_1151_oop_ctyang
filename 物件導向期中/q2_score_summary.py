# -*- coding: utf-8 -*-
"""
第二題：成績清單摘要函式（30 分）

題目要求：
完成函式 print_score_summary(scores, passing_score)。函式接收一個整數串列與及格門檻，依序印出：
筆數：...
總分：...
平均：...
及格人數：...
"""

def print_score_summary(scores, passing_score):
    """
    計算並印出成績清單的摘要資訊。
    
    參數:
        scores (list): 包含整數分數的串列（題目保證至少有一個分數）
        passing_score (int): 及格門檻分數
    """
    # 步驟 2: 設定總分與及格人數的初始值
    total_score = 0
    passing_count = 0
    
    # 步驟 3 & 4: 走訪 scores，累加總分並判斷是否達到及格門檻
    for score in scores:
        total_score += score
        if score >= passing_score:
            passing_count += 1
            
    # 步驟 5: 走訪完後計算平均（直接使用除法計算，不需自行四捨五入）
    count = len(scores)
    average = total_score / count
    
    # 步驟 6: 用 len(scores) 取得筆數，再用 f-string 輸出四行摘要
    print(f"筆數：{count}")
    print(f"總分：{total_score}")
    print(f"平均：{average}")
    print(f"及格人數：{passing_count}")


if __name__ == "__main__":
    print("=" * 40)
    print("測試 1（題目範例）：")
    print("=" * 40)
    scores1 = [72, 90, 64, 88, 96]
    print_score_summary(scores1, 70)
    
    print("\n" + "=" * 40)
    print("測試 2（題目自行測試範例，含等於門檻）：")
    print("=" * 40)
    scores2 = [50, 60, 70]
    print_score_summary(scores2, 60)
    
    print("\n" + "=" * 40)
    print("測試 3（額外邊界測試：全及格）：")
    print("=" * 40)
    scores3 = [100, 95, 80]
    print_score_summary(scores3, 60)
    
    print("\n" + "=" * 40)
    print("測試 4（額外邊界測試：全不及格）：")
    print("=" * 40)
    scores4 = [30, 45, 59]
    print_score_summary(scores4, 60)
