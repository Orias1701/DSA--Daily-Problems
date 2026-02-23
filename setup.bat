@echo off
chcp 65001 >nul
echo Đang setup môi trường ảo...
python setup_venv.py
if errorlevel 1 (
    echo.
    echo Lỗi. Kiểm tra đã cài Python và đã thêm Python vào PATH.
    pause
    exit /b 1
)
echo.
pause
