@echo off
chcp 65001 >nul
title 特徵敏感度分析工具 — 安裝並執行

echo =================================================
echo   特徵敏感度分析工具  ^|  物件導向期中報告
echo =================================================
echo.

:: 切換到腳本所在目錄
cd /d "%~dp0"

:: 確認 Python 是否存在
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！
    echo 請先安裝 Python 3.8 以上版本：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 確認 Python 版本...
python --version

echo.
echo [2/3] 安裝必要套件（若已安裝則跳過）...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [錯誤] 套件安裝失敗！請確認網路連線，或手動執行：
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo       套件安裝完成 ✓

echo.
echo [3/3] 執行主程式...
echo -------------------------------------------------
python sensitivity_tool.py
echo -------------------------------------------------

echo.
echo 分析完成！輸出圖片：
echo   result_small.png  ^(小資料 49 筆^)
echo   result_full.png   ^(大資料 5094 筆^)
echo.
pause
