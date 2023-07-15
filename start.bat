echo off
chcp 65001

if not exist "venv" (
	echo 創建執行環境
	py -m venv venv
)
call venv\Scripts\activate

echo 下載程式需求的模組
pip install -r requirements.txt

echo.

py main.py
pause