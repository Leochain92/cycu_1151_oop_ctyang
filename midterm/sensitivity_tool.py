# =============================================================================
# sensitivity_tool.py
# 特徵敏感度分析工具 ── 物件導向程式設計期中報告
# 作者：學生
# 功能：對土壤含水量預測的輸入特徵（R, G, B, H, S, V）進行敏感度分析，
#       比較「相關係數法」與「Sobol pick-freeze 法」的差異。
# =============================================================================

# ── 第一節：必要套件匯入與常數定義 ─────────────────────────────────────────

import os
import math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
# 設定中文字型（優先使用微軟正黑體，確保中文正常顯示）
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
from sklearn.neighbors import KNeighborsRegressor

# 特徵顏色對應（長條圖用）
FEATURE_COLORS = {
    'R': '#E74C3C',   # 紅
    'G': '#27AE60',   # 綠
    'B': '#2980B9',   # 藍
    'H': '#E67E22',   # 橙
    'S': '#8E44AD',   # 紫
    'V': '#F1C40F',   # 黃
}

# 預設特徵名稱順序
DEFAULT_FEATURES = ['R', 'G', 'B', 'H', 'S', 'V']


# ── 第二節：資料載入函式 ────────────────────────────────────────────────────

def load_data(csv_path):
    """
    讀取 CSV，回傳 X(numpy array, shape NxF) 和 y(numpy array)。

    參數
    ----
    csv_path : str
        CSV 檔案路徑，需包含欄位 R, G, B, H, S, V, WaterContent

    回傳
    ----
    X : numpy.ndarray  shape (N, 6)
        六個輸入特徵矩陣
    y : numpy.ndarray  shape (N,)
        目標變數（土壤含水量）
    feature_names : list[str]
        特徵名稱清單
    """
    df = pd.read_csv(csv_path)
    feature_names = ['R', 'G', 'B', 'H', 'S', 'V']
    X = df[feature_names].values.astype(float)
    y = df['WaterContent'].values.astype(float)
    return X, y, feature_names


# ── 第三節：相關係數法敏感度 ────────────────────────────────────────────────

def _pearson_r2(x_col, y):
    """計算單一特徵與 y 的 Pearson r^2（決定係數）。"""
    n = len(x_col)
    if n == 0:
        return 0.0
    mean_x = sum(x_col) / n
    mean_y = sum(y) / n
    cov  = sum((x_col[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    std_x = math.sqrt(sum((x_col[i] - mean_x)**2 for i in range(n)))
    std_y = math.sqrt(sum((y[i] - mean_y)**2 for i in range(n)))
    if std_x < 1e-12 or std_y < 1e-12:
        return 0.0
    r = cov / (std_x * std_y)
    return r * r


def _cond_var_sensitivity(x_col, y):
    """
    分箱條件變異數法（Sobol ST 的簡化近似）。

    做法：以 33 與 67 百分位數為切點，取低段和高段的 y，
    計算條件變異數，估計總階敏感度。
    ST[i] ≈ 1 - (Var(y|low) + Var(y|high)) / (2 * Var(y))
    """
    x_sorted = sorted(x_col)
    n = len(x_sorted)
    p33 = x_sorted[int(0.33 * n)]
    p67 = x_sorted[int(0.67 * n)]

    y_low  = [y[i] for i in range(n) if x_col[i] <= p33]
    y_high = [y[i] for i in range(n) if x_col[i] >= p67]

    def _var(lst):
        if len(lst) < 2:
            return 0.0
        m = sum(lst) / len(lst)
        return sum((v - m)**2 for v in lst) / (len(lst) - 1)

    total_var = _var(list(y))
    if total_var < 1e-12:
        return 0.0
    # 兩組條件變異數的平均
    avg_cond_var = (_var(y_low) + _var(y_high)) / 2.0
    st_approx = 1.0 - avg_cond_var / total_var
    return max(0.0, st_approx)   # 限制不低於 0


def corr_sensitivity(X, y, feature_names):
    """
    方法 1：相關係數平方法 + 分箱條件變異數法。

    - corr_sq ：各特徵的 Pearson r^2，代表一階線性敏感度。
    - cond_var：分箱條件變異數法，近似 Sobol 總階敏感度 (ST)。

    參數
    ----
    X : numpy.ndarray  (N, F)
    y : numpy.ndarray  (N,)
    feature_names : list[str]

    回傳
    ----
    result : dict
        'corr_sq'  : list[float]  各特徵 r^2
        'cond_var' : list[float]  各特徵條件變異數敏感度
    """
    n_features = X.shape[1]
    corr_sq  = []
    cond_var = []

    for i in range(n_features):
        x_col = list(X[:, i])
        y_list = list(y)
        corr_sq.append(_pearson_r2(x_col, y_list))
        cond_var.append(_cond_var_sensitivity(x_col, y_list))

    return {'corr_sq': corr_sq, 'cond_var': cond_var}


# ── 第四節：Sobol pick-freeze 法 ────────────────────────────────────────────

def sobol_indices(X, y_func, n_samples=4096, seed=42):
    """
    方法 2：Saltelli pick-freeze 方案計算 Sobol 一階（S1）與總階（ST）敏感度。

    演算法：
      1. 用各特徵的 [min, max] 範圍建立均勻分布樣本矩陣 A, B（各 n_samples 列）。
      2. 對每個特徵 i 建立混合矩陣 AB_i（A 的所有欄 + 用 B 的第 i 欄取代）。
      3. 計算 y_A, y_B, y_AB_i 三組輸出。
      4. Jansen 估計量：
           S1[i] = Var(y_A) - 0.5 * mean((y_B - y_AB_i)^2) / Var(y_A)
                   ≈ mean(y_B * (y_AB_i - y_A)) / Var(y_A)
           ST[i] = 0.5 * mean((y_A - y_AB_i)^2) / Var(y_A)

    參數
    ----
    X      : numpy.ndarray  原始資料（僅用於估計特徵範圍）
    y_func : callable       接受 (N, F) numpy array，回傳長度 N 的預測向量
    n_samples : int         每組樣本數（建議 512 以上）
    seed   : int            亂數種子，確保結果可重現

    回傳
    ----
    result : dict
        'S1' : numpy.ndarray  一階 Sobol 指標
        'ST' : numpy.ndarray  總階 Sobol 指標
    """
    rng = np.random.default_rng(seed)
    n_features = X.shape[1]

    # 用特徵的 min / max 估計採樣範圍
    x_min = X.min(axis=0)
    x_max = X.max(axis=0)

    # 建立 A, B 兩組隨機樣本（均勻分布）
    A = rng.uniform(0, 1, size=(n_samples, n_features)) * (x_max - x_min) + x_min
    B = rng.uniform(0, 1, size=(n_samples, n_features)) * (x_max - x_min) + x_min

    # 評估 A 和 B
    y_A = y_func(A)
    y_B = y_func(B)

    var_y = float(np.var(y_A))
    if var_y < 1e-12:
        # 若方差近零，所有敏感度設為 0
        return {'S1': np.zeros(n_features), 'ST': np.zeros(n_features)}

    S1 = np.zeros(n_features)
    ST = np.zeros(n_features)

    for i in range(n_features):
        # AB_i：A 的所有欄，第 i 欄換成 B 的第 i 欄
        AB_i = A.copy()
        AB_i[:, i] = B[:, i]

        y_AB_i = y_func(AB_i)

        # Jansen 估計量（數值穩定性較好）
        S1[i] = (np.mean(y_B * (y_AB_i - y_A))) / var_y
        ST[i] = (0.5 * np.mean((y_A - y_AB_i) ** 2)) / var_y

        # 修正：S1 可能因數值誤差略小於 0，截斷
        S1[i] = max(0.0, S1[i])
        ST[i] = max(0.0, ST[i])

    return {'S1': S1, 'ST': ST}


# ── 第五節：驗證函式（已知函數測試）────────────────────────────────────────

def _table_row(name, vals):
    """格式化輸出一列資料（標頭列或數值列）。"""
    vals_list = list(vals)
    if vals_list and isinstance(vals_list[0], str):
        # 標頭列：字串對齊
        formatted = '  '.join(f'{v:>6s}' for v in vals_list)
    else:
        # 數值列：浮點格式
        formatted = '  '.join(f'{float(v):6.3f}' for v in vals_list)
    return f'  {name:<16s}  {formatted}'


def verify_with_known_functions():
    """
    用三個已知解析函數驗證兩種方法的準確度。

    函數 1 — 線性函數：y = 3*x1 + x2 + 0.5*x3
        x1 係數最大，應有最高敏感度。

    函數 2 — 交互作用：y = x1*x2 + x3
        x1, x2 的交互作用項使相關係數法低估；x3 為線性主效應。

    函數 3 — Ishigami 函數：y = sin(x1) + 7*sin²(x2) + 0.1*x3⁴*sin(x1)
        已知解：S1=[0.314, 0.442, 0], ST=[0.558, 0.442, 0.244]
        x3 只透過交互作用影響輸出，S1=0 但 ST>0。

    印出比較表，顯示兩種方法的差異。
    """
    print('\n' + '=' * 65)
    print('  第五節：已知函數驗證')
    print('=' * 65)

    rng = np.random.default_rng(0)
    N_VALID = 2000   # 驗證用樣本數

    # ── 函數 1：線性函數 ────────────────────────────────────────
    print('\n[函數 1] y = 3*x1 + x2 + 0.5*x3  (均勻分布 [0,1])')
    print('  預期：x1 敏感度最高，x2 次之，x3 最低')

    X1 = rng.uniform(0, 1, size=(N_VALID, 3))
    y1 = 3 * X1[:, 0] + X1[:, 1] + 0.5 * X1[:, 2]

    corr1 = corr_sensitivity(X1, y1, ['x1', 'x2', 'x3'])
    knn1 = KNeighborsRegressor(n_neighbors=5)
    knn1.fit(X1, y1)
    sobol1 = sobol_indices(X1, knn1.predict, n_samples=1024, seed=0)

    print('  ' + '-' * 61)
    print(_table_row('方法 \\ 特徵', ['x1', 'x2', 'x3']))
    print('  ' + '-' * 61)
    print(_table_row('相關係數 r^2', corr1['corr_sq']))
    print(_table_row('條件變異數', corr1['cond_var']))
    print(_table_row('Sobol S1', sobol1['S1']))
    print(_table_row('Sobol ST', sobol1['ST']))

    # ── 函數 2：交互作用 ────────────────────────────────────────
    print('\n[函數 2] y = x1*x2 + x3  (均勻分布 [0,1])')
    print('  預期：相關係數法低估 x1, x2 的交互作用；Sobol ST 能捕捉')

    X2 = rng.uniform(0, 1, size=(N_VALID, 3))
    y2 = X2[:, 0] * X2[:, 1] + X2[:, 2]

    corr2 = corr_sensitivity(X2, y2, ['x1', 'x2', 'x3'])
    knn2 = KNeighborsRegressor(n_neighbors=5)
    knn2.fit(X2, y2)
    sobol2 = sobol_indices(X2, knn2.predict, n_samples=1024, seed=0)

    print('  ' + '-' * 61)
    print(_table_row('方法 \\ 特徵', ['x1', 'x2', 'x3']))
    print('  ' + '-' * 61)
    print(_table_row('相關係數 r^2', corr2['corr_sq']))
    print(_table_row('條件變異數', corr2['cond_var']))
    print(_table_row('Sobol S1', sobol2['S1']))
    print(_table_row('Sobol ST', sobol2['ST']))

    # ── 函數 3：Ishigami ────────────────────────────────────────
    print('\n[函數 3] Ishigami: y = sin(x1) + 7*sin^2(x2) + 0.1*x3^4*sin(x1)')
    print('  xi ~ Uniform[-pi, pi]')
    print('  理論解  S1=[0.314, 0.442, 0.000]  ST=[0.558, 0.442, 0.244]')

    X3 = rng.uniform(-math.pi, math.pi, size=(N_VALID, 3))
    y3 = (np.sin(X3[:, 0])
          + 7 * np.sin(X3[:, 1])**2
          + 0.1 * X3[:, 2]**4 * np.sin(X3[:, 0]))

    corr3 = corr_sensitivity(X3, y3, ['x1', 'x2', 'x3'])
    knn3 = KNeighborsRegressor(n_neighbors=5)
    knn3.fit(X3, y3)
    sobol3 = sobol_indices(X3, knn3.predict, n_samples=2048, seed=0)

    print('  ' + '-' * 61)
    print(_table_row('方法 \\ 特徵', ['x1', 'x2', 'x3']))
    print('  ' + '-' * 61)
    print(_table_row('相關係數 r^2', corr3['corr_sq']))
    print(_table_row('條件變異數', corr3['cond_var']))
    print(_table_row('Sobol S1', sobol3['S1']))
    print(_table_row('Sobol ST', sobol3['ST']))
    print(_table_row('理論 S1', [0.314, 0.442, 0.000]))
    print(_table_row('理論 ST', [0.558, 0.442, 0.244]))
    print()


# ── 第六節：視覺化函式 ──────────────────────────────────────────────────────

def plot_comparison(corr_result, sobol_result, feature_names, title, save_path):
    """
    繪製並儲存敏感度比較圖。

    左圖：相關係數法（corr_sq vs cond_var）長條圖
    右圖：Sobol pick-freeze（S1 vs ST）長條圖

    顏色對應：R=紅, G=綠, B=藍, H=橙, S=紫, V=黃

    參數
    ----
    corr_result  : dict  corr_sensitivity() 的回傳值
    sobol_result : dict  sobol_indices() 的回傳值
    feature_names: list[str]
    title        : str   圖表主標題
    save_path    : str   輸出圖片路徑（.png）
    """
    n = len(feature_names)
    x_pos = np.arange(n)
    width = 0.35

    # 取得對應顏色
    colors = [FEATURE_COLORS.get(f, '#95A5A6') for f in feature_names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, fontsize=14, fontweight='bold')

    # ── 左圖：相關係數法 ─────────────────────────────────────────
    bars1a = ax1.bar(x_pos - width / 2,
                     corr_result['corr_sq'],
                     width,
                     label='Pearson $r^2$ (一階)',
                     color=colors,
                     alpha=0.85,
                     edgecolor='black',
                     linewidth=0.6)
    bars1b = ax1.bar(x_pos + width / 2,
                     corr_result['cond_var'],
                     width,
                     label='條件變異數 (近似 ST)',
                     color=colors,
                     alpha=0.4,
                     edgecolor='black',
                     linewidth=0.6,
                     hatch='//')

    ax1.set_title('方法 1：相關係數法', fontsize=12)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(feature_names, fontsize=11)
    ax1.set_ylabel('敏感度指標值', fontsize=10)
    ax1.set_ylim(0, 1.0)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    # ── 右圖：Sobol pick-freeze ───────────────────────────────────
    bars2a = ax2.bar(x_pos - width / 2,
                     sobol_result['S1'],
                     width,
                     label='S1（一階）',
                     color=colors,
                     alpha=0.85,
                     edgecolor='black',
                     linewidth=0.6)
    bars2b = ax2.bar(x_pos + width / 2,
                     sobol_result['ST'],
                     width,
                     label='ST（總階）',
                     color=colors,
                     alpha=0.4,
                     edgecolor='black',
                     linewidth=0.6,
                     hatch='//')

    ax2.set_title('方法 2：Sobol pick-freeze 法', fontsize=12)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(feature_names, fontsize=11)
    ax2.set_ylabel('Sobol 指標值', fontsize=10)
    ax2.set_ylim(0, 1.0)
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    # 顏色圖例（特徵對應）
    legend_patches = [
        mpatches.Patch(color=FEATURE_COLORS.get(f, '#95A5A6'), label=f)
        for f in feature_names
    ]
    fig.legend(handles=legend_patches,
               loc='lower center',
               ncol=n,
               fontsize=9,
               title='特徵顏色對應',
               bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  圖片已儲存：{save_path}')


def _print_ranking(corr_result, sobol_result, feature_names):
    """印出特徵重要性排名（依 Sobol ST 降序）。"""
    st_vals = sobol_result['ST']
    ranking = sorted(zip(feature_names, corr_result['corr_sq'],
                         corr_result['cond_var'],
                         sobol_result['S1'], st_vals),
                     key=lambda t: t[4], reverse=True)

    print('\n  特徵重要性排名（依 Sobol ST 降序）：')
    print(f'  {"排名":<4} {"特徵":<6} {"r^2":>7} {"CondVar":>9} {"S1":>7} {"ST":>7}')
    print('  ' + '-' * 44)
    for rank, (feat, r2, cv, s1, st) in enumerate(ranking, 1):
        print(f'  {rank:<4} {feat:<6} {r2:>7.3f} {cv:>9.3f} {s1:>7.3f} {st:>7.3f}')


# ── 第七節：main() 主流程 ───────────────────────────────────────────────────

def main():
    """
    主流程：
      1. 驗證：用三個已知函數測試兩種方法
      2. 小資料示範（49 筆）：載入 -> 分析 -> 繪圖 -> 排名
      3. 大資料示範（5094 筆）：同上流程
    """
    print('=' * 65)
    print('  特徵敏感度分析工具')
    print('  用途：比較「相關係數法」與「Sobol pick-freeze 法」')
    print('        對土壤含水量預測輸入特徵（R,G,B,H,S,V）的敏感度')
    print('=' * 65)

    # ── 步驟 1：驗證 ─────────────────────────────────────────────
    verify_with_known_functions()

    # 取得腳本所在目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ── 步驟 2：小資料示範（49 筆）───────────────────────────────
    small_csv = os.path.join(base_dir, 'soil_small_49x6.csv')
    print('\n' + '=' * 65)
    print('  步驟 2：小資料示範 (soil_small_49x6.csv，49 筆)')
    print('=' * 65)

    X_s, y_s, feat_names = load_data(small_csv)
    print(f'  資料形狀：X={X_s.shape}, y={y_s.shape}')

    # 相關係數法（直接用真實 WaterContent）
    print('  執行相關係數法...')
    corr_s = corr_sensitivity(X_s, y_s, feat_names)

    # Sobol pick-freeze（KNN 做資料驅動的 y_func）
    print('  訓練 KNN（k=5）以近似 y_func...')
    knn_s = KNeighborsRegressor(n_neighbors=5)
    knn_s.fit(X_s, y_s)

    print('  執行 Sobol pick-freeze（n=512）...')
    sobol_s = sobol_indices(X_s, knn_s.predict, n_samples=512, seed=42)

    # 繪圖
    save_small = os.path.join(base_dir, 'result_small.png')
    plot_comparison(corr_s, sobol_s, feat_names,
                    '土壤含水量特徵敏感度分析（小資料，49 筆）',
                    save_small)

    # 排名
    _print_ranking(corr_s, sobol_s, feat_names)

    # ── 步驟 3：大資料示範（5094 筆）────────────────────────────
    full_csv = os.path.join(base_dir, 'soil_full_5094x6.csv')
    print('\n' + '=' * 65)
    print('  步驟 3：大資料示範 (soil_full_5094x6.csv，5094 筆)')
    print('=' * 65)

    X_f, y_f, feat_names = load_data(full_csv)
    print(f'  資料形狀：X={X_f.shape}, y={y_f.shape}')

    # 相關係數法
    print('  執行相關係數法...')
    corr_f = corr_sensitivity(X_f, y_f, feat_names)

    # KNN y_func
    print('  訓練 KNN（k=5）...')
    knn_f = KNeighborsRegressor(n_neighbors=5)
    knn_f.fit(X_f, y_f)

    print('  執行 Sobol pick-freeze（n=2048）...')
    sobol_f = sobol_indices(X_f, knn_f.predict, n_samples=2048, seed=42)

    # 繪圖
    save_full = os.path.join(base_dir, 'result_full.png')
    plot_comparison(corr_f, sobol_f, feat_names,
                    '土壤含水量特徵敏感度分析（大資料，5094 筆）',
                    save_full)

    # 排名
    _print_ranking(corr_f, sobol_f, feat_names)

    print('\n' + '=' * 65)
    print('  全部流程完成！')
    print(f'  輸出圖片：result_small.png, result_full.png')
    print('=' * 65)


# ── 程式進入點 ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    main()
