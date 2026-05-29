@echo off
chcp 65001 >nul
title AI Agents Manager - Запуск
color 0F

echo ========================================
echo    AI Agents Manager
echo    Автоматический запуск
echo ========================================
echo.
echo Запуск скрипта...
echo.

:: Создаем файл логов
set LOGFILE=%~dp0launch_log.txt
echo ============ Запуск в %date% %time% ============ > %LOGFILE%

:: Проверка Python
echo [1/6] Проверка Python...
echo [1/6] Проверка Python... >> %LOGFILE%
python --version 2>&1 | tee -a %LOGFILE%
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python не найден!
    echo.
    echo Установите Python с https://python.org
    echo При установке ОБЯЗАТЕЛЬНО поставьте галочку:
    echo "Add Python to PATH"
    echo.
    echo Файл лога: %LOGFILE%
    echo.
    pause
    exit /b 1
)
echo [OK] Python найден
echo [OK] Python найден >> %LOGFILE%
echo.

:: Проверка Node.js
echo [2/6] Проверка Node.js...
echo [2/6] Проверка Node.js... >> %LOGFILE%
node --version 2>&1 | tee -a %LOGFILE%
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js не найден!
    echo.
    echo Установите Node.js с https://nodejs.org
    echo.
    echo Файл лога: %LOGFILE%
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js найден
echo [OK] Node.js найден >> %LOGFILE%
echo.

:: Переход в backend
cd backend
echo [3/6] Переход в backend...
echo [3/6] Переход в backend... >> %LOGFILE%

:: Виртуальное окружение
echo [3/6] Проверка виртуального окружения...
echo [3/6] Проверка виртуального окружения... >> %LOGFILE%
if not exist "venv\" (
    echo Создаю виртуальное окружение (это займет ~1 минуту)...
    echo Создаю виртуальное окружение... >> %LOGFILE%
    python -m venv venv 2>&1 | tee -a %LOGFILE%
    echo [OK] Виртуальное окружение создано
    echo [OK] Виртуальное окружение создано >> %LOGFILE%
) else (
    echo [OK] Виртуальное окружение уже есть
    echo [OK] Виртуальное окружение уже есть >> %LOGFILE%
)
echo.

:: Активация
echo [4/6] Активация окружения...
echo [4/6] Активация окружения... >> %LOGFILE%
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Не удалось активировать виртуальное окружение!
    echo.
    echo Файл лога: %LOGFILE%
    echo.
    pause
    exit /b 1
)
echo [OK] Окружение активно
echo [OK] Окружение активно >> %LOGFILE%
echo.

:: Зависимости
echo [5/6] Проверка зависимостей...
echo [5/6] Проверка зависимостей... >> %LOGFILE%
if not exist "venv\Lib\site-packages\fastapi" (
    echo Устанавливаю зависимости (это может занять 3-5 минут)...
    echo Устанавливаю зависимости... >> %LOGFILE%
    pip install -r requirements.txt 2>&1 | tee -a %LOGFILE%
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Ошибка установки зависимостей!
        echo.
        echo Проверьте файл лога: %LOGFILE%
        echo.
        pause
        exit /b 1
    )
    echo [OK] Зависимости установлены
    echo [OK] Зависимости установлены >> %LOGFILE%
) else (
    echo [OK] Зависимости уже установлены
    echo [OK] Зависимости уже установлены >> %LOGFILE%
)
echo.

:: .env файл
if not exist ".env" (
    echo Создаю файл .env...
    echo Создаю файл .env... >> %LOGFILE%
    (echo APP_NAME=^"AI Agents Manager^") > .env
    (echo DATABASE_URL=sqlite:///./ai_agents.db) >> .env
    (echo SECRET_KEY=your-secret-key-change-in-production) >> .env
    (echo BACKEND_CORS_ORIGINS=["http://localhost:3000"]) >> .env
    echo [OK] Файл .env создан
    echo [OK] Файл .env создан >> %LOGFILE%
)
echo.

echo ========================================
echo [6/6] Запуск Backend...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Запускаю Backend в отдельном окне...
echo Запускаю Backend... >> %LOGFILE%

:: Запуск backend в новом окне с видимым окном
start "AI Agents - Backend Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && echo Backend запущен... && echo Лог: %LOGFILE% && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Переход к Frontend...
echo ========================================
echo.

cd ..\frontend
echo Проверка Frontend зависимостей...
echo Проверка Frontend зависимостей... >> %LOGFILE%

if not exist "node_modules\" (
    echo Устанавливаю Frontend зависимости (это может занять 3-5 минут)...
    echo Устанавливаю Frontend зависимости... >> %LOGFILE%
    call npm install 2>&1 | tee -a %LOGFILE%
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Ошибка установки Frontend зависимостей!
        echo.
        echo Проверьте файл лога: %LOGFILE%
        echo.
        pause
        exit /b 1
    )
    echo [OK] Frontend зависимости установлены
    echo [OK] Frontend зависимости установлены >> %LOGFILE%
) else (
    echo [OK] Frontend зависимости уже установлены
    echo [OK] Frontend зависимости уже установлены >> %LOGFILE%
)

echo.
echo ========================================
echo ЗАПУЩЕНО!
echo ========================================
echo.
echo SUCCESS: Все компоненты успешно запущены!
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Откройте http://localhost:3000 в браузере!
echo.
echo Лог выполнения: %LOGFILE%
echo.
echo ========================================
echo Окно не закроется автоматически.
echo Нажмите любую клавишу для остановки Frontend
echo ========================================
echo.

call npm run dev

echo.
echo ========================================
echo Frontend остановлен
echo ========================================
echo.
pause