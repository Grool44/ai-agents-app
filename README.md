# AI Agents Manager

Умная платформа для управления AI-агентами с 2D пиксельной графикой.

## 🚀 Быстрый старт

### Локальный запуск:

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (в новом окне)
cd frontend
python -m http.server 3000
```

Открой: http://localhost:3000

## 🌐 Деплой на Render.com

### 1. Подготовь репозиторий:

Все файлы уже настроены:
- ✅ `requirements.txt` - зависимости в корне
- ✅ `backend/requirements.txt` - зависимости backend
- ✅ `render.yaml` - конфигурация для Render

### 2. Создай Web Service на Render:

1. Зайди на [render.com](https://render.com)
2. `New +` → `Web Service`
3. Подключи GitHub репозиторий
4. Настройки:
   - **Name**: `ai-agents-app`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. Добавь переменные окружения (опционально):
   ```
   AI_API_KEY=твой_api_key
   AI_MODEL=deepseek/deepseek-chat
   ```

6. Нажми `Create Web Service`

### 3. После деплоя:

- Backend API: `https://твой-домен.onrender.com/api/v1`
- Frontend нужно развернуть отдельно (см. ниже)

## 🌍 Деплой Frontend

### Вариант 1: Vercel (рекомендую)

```bash
npm i -g vercel
cd frontend
vercel
```

В `vercel.json` укажи API URL:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Измени `frontend/dashboard.html`:
```javascript
const API_BASE = "https://твой-backend.onrender.com/api/v1";
```

### Вариант 2: Netlify

```bash
npm i -g netlify-cli
cd frontend
netlify deploy --prod
```

## 📁 Структура проекта

```
ai-agents-app/
├── backend/
│   ├── main.py           # FastAPI сервер
│   ├── requirements.txt  # Зависимости
│   └── .env             # API ключи (не пушить!)
├── frontend/
│   ├── dashboard.html    # Главный интерфейс
│   ├── css/style.css     # Стили
│   └── js/auth.js        # Авторизация
├── requirements.txt      # Зависимости для Render
├── render.yaml          # Конфигурация Render
└── README.md
```

## 🔧 Настройка AI

Добавь в `.env` в `backend/`:

```env
AI_API_KEY=sk-or-твой_ключ_от_openrouter
AI_MODEL=deepseek/deepseek-chat
AI_BASE_URL=https://openrouter.ai/api/v1
```

Без API ключа агенты работают в режиме шаблонов.

## 🎨 Особенности

- 2D пиксельная графика с анимацией
- Переключение режимов: Pixel ↔ Modern
- Динамическое расположение агентов
- Генерация изображений агентами (с API ключом)
- Голосовой ввод сообщений
- Система задач и чатов

## 📝 Лицензия

MIT License

