@echo off
chcp 65001 >nul
title AI Agents Manager - Запуск

echo ========================================
echo    AI Agents Manager
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите с https://python.org
echo При установке поставьте галочку "Add Python to PATH"
    pause
    exit /b 1
)

:: Переход в backend
cd backend

:: Создание venv если нет
if not exist "venv\" (
    echo [1/3] Создание виртуального окружения...
    python -m venv venv
)

:: Активация
call venv\Scripts\activate

:: Установка зависимостей
if not exist "venv\Lib\site-packages\fastapi" (
    echo [2/3] Установка зависимостей...
    pip install -r requirements.txt --quiet
)

:: Создание .env если нет
if not exist ".env" (
    echo [3/3] Создание .env...
    copy .env.example .env >nul
    echo [WARN] Создан .env из шаблона. Отредактируйте backend/.env и укажите свои API-ключи!
)

echo.
echo ========================================
echo Запуск Backend...
echo ========================================
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
start "AI Agents - Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Запуск Frontend сервера...
echo ========================================
echo Frontend: http://localhost:3000
echo.
cd ..\frontend
start "AI Agents - Frontend" cmd /k "cd /d %~dp0frontend && python -m http.server 3000"

echo.
echo ========================================
echo Все сервисы запущены!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause