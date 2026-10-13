import numpy as np

def solve_inverse(matrix):
    """
    計算並回傳 square matrix 的反矩陣。
    
    參數:
        matrix: 輸入的 n x n 矩陣 (numpy.ndarray 或 list of lists)
        
    回傳:
        numpy.ndarray: 反矩陣
    """
    # 1. 確保矩陣為浮點數型態 (float)
    mat = np.array(matrix, dtype=float)
    
    # 2. 確保矩陣為方陣 (n x n)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError("輸入必須為 n x n 的方陣")
        
    # 3. 執行反矩陣計算，若為不可逆矩陣則 raise ValueError
    try:
        inv_matrix = np.linalg.inv(mat)
        return inv_matrix
    except np.linalg.LinAlgError:
        raise ValueError("此為不可逆矩陣 (det 為 0 或主對角線無法找到 pivot)")

# ================= 測試與驗證區域 =================
if __name__ == "__main__":
    test_matrix = np.array([
        [6, 3, 7, 4, 6, 9, 2, 6, 7, 4],
        [3, 7, 7, 2, 5, 4, 1, 7, 5, 1],
        [4, 0, 9, 5, 8, 0, 9, 2, 6, 3],
        [8, 2, 4, 2, 6, 4, 8, 6, 1, 3],
        [8, 1, 9, 8, 9, 4, 1, 3, 6, 7],
        [2, 0, 3, 1, 7, 3, 1, 5, 5, 9],
        [3, 5, 1, 9, 1, 9, 3, 7, 6, 8],
        [7, 4, 1, 4, 7, 9, 8, 8, 0, 8],
        [6, 8, 7, 0, 7, 7, 2, 0, 7, 2],
        [2, 0, 4, 9, 6, 9, 8, 6, 8, 7]
    ], dtype=float)
    
    # 執行反矩陣計算
    inv = solve_inverse(test_matrix)
    
    # 檢查 A @ A^(-1) 是否接近單位矩陣 I
    identity = np.eye(len(test_matrix))
    is_correct = np.allclose(test_matrix @ inv, identity, atol=1e-7)
    
    print("反矩陣計算結果:")
    print(inv)
    print("反矩陣計算結果形狀:", inv.shape)
    print("驗證 A @ A^(-1) == I :", "成功 (Pass)" if is_correct else "失敗 (Fail)")