@echo off
echo Установка прокси для Python...
set HTTP_PROXY=http://127.0.0.1:10808
set HTTPS_PROXY=http://127.0.0.1:10808
set ALL_PROXY=http://127.0.0.1:10808

echo Запуск бота...
python main.py
pause