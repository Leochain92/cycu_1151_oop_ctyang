# 特徵敏感度分析小工具
**物件導向程式設計 — 期中報告**

> 白話說明：用 R、G、B、H、S、V 六個顏色數字預測土壤含水量，
> 比較兩種方法來判斷「哪個數字最重要」：
> - 方法 1：相關係數法（r²）＋ 分箱條件變異數
> - 方法 2：Sobol pick-freeze（變異數分解，更嚴謹）

---

## 快速開始

### 方法 A：一鍵安裝並執行（Windows，推薦）
```
雙擊執行  →  setup_and_run.bat
```

### 方法 B：手動執行
```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 執行主程式
python sensitivity_tool.py
```

### 方法 C：用虛擬環境（最乾淨，不影響系統套件）
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python sensitivity_tool.py
```

---

## 執行結果

程式執行後會：
1. 在終端機印出三個已知函數的驗證結果
2. 印出小資料（49 筆）和大資料（5094 筆）的特徵重要性排名
3. 在同目錄產生 `result_small.png` 和 `result_full.png`

---

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `sensitivity_tool.py` | 主程式（7 節架構，純函式設計） |
| `soil_small_49x6.csv` | 小測試資料（49 列，分層抽樣，seed=42） |
| `soil_full_5094x6.csv` | 真實規模資料（5094 列，Train+Val+Test） |
| `requirements.txt` | Python 套件需求 |
| `setup_and_run.bat` | Windows 一鍵啟動腳本 |

---

## 套件需求

| 套件 | 用途 |
|------|------|
| numpy | 數值計算（矩陣、亂數） |
| pandas | 讀取 CSV |
| matplotlib | 繪圖 |
| scikit-learn | KNN（資料驅動 y_func） |
| openpyxl | 讀取 Excel（生成 CSV 用） |

Python 版本：**3.8 以上**

---

## 研究背景

- **資料來源**：自行拍攝紅土影像（Full 與 ROI，8 種光源），搭配 CNN/ANN/SVM 模型
- **6 個特徵**：影像的 R、G、B（RGB 色彩空間）和 H、S、V（HSV 色彩空間）平均值
- **目標變數**：土壤含水量（%），7 個水準：12.0、18.4、22.4、24.8、28.5、37.2、46.1

---

## 作者
物件導向程式設計期中報告 © 2026
