from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Agents Manager", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CONFIG ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
AGENTS_FILE = os.path.join(DATA_DIR, "agents.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
VISITS_FILE = os.path.join(DATA_DIR, "visits.json")

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek/deepseek-chat")

# === HELPERS ===
def load_json(filepath: str, default: list = None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Load JSON error: {e}")
    return default

def save_json(filepath: str, data: list):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def now_ms() -> int:
    return int(datetime.now().timestamp() * 1000)

# === SYSTEM PROMPTS ===
SYSTEM_PROMPTS = {
    "ceo": (
        "Ты — Генеральный директор ИИ-компании. Ты управляешь командой специализированных агентов: "
        "Coder (программирование), Researcher (поиск информации), Analyst (анализ данных), Poster (публикации). "
        "Ты умеешь анализировать задачи и распределять их. Отвечай профессионально, по делу, как опытный руководитель."
    ),
    "coder": (
        "Ты — опытный программист. Ты пишешь код на Python, JavaScript, SQL. Ты умеешь объяснять сложное простым языком, "
        "давать готовые примеры кода с комментариями. Используй markdown для форматирования кода."
    ),
    "researcher": (
        "Ты — исследователь. Ты ищешь информацию, анализируешь источники, делаешь выжимки. "
        "Отвечай структурированно, с фактами, разбивай на пункты."
    ),
    "analyst": (
        "Ты — аналитик данных. Ты умеешь: строить отчёты, находить инсайты, визуализировать данные текстом, "
        "делать прогнозы. Отвечай с цифрами и логикой."
    ),
    "poster": (
        "Ты — контент-мейкер. Ты пишешь посты для соцсетей, придумываешь хештеги, заголовки, описания. "
        "Твой текст должен быть цепляющим и вирусным."
    ),
}

# === AI SERVICE ===
def call_real_ai(messages: List[Dict[str, str]], model: str = None) -> Optional[str]:
    """Вызов реального LLM через OpenAI-compatible API."""
    if not AI_API_KEY:
        return None
    if model is None:
        model = AI_MODEL

    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Agents Manager",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        resp = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"AI API error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"AI call error: {e}")
    return None

def generate_image(prompt: str) -> Optional[str]:
    """Генерация изображения через DALL-E или аналогичный API."""
    if not AI_API_KEY:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": f"Create an image for: {prompt}",
            "n": 1,
            "size": "1024x1024",
        }
        resp = requests.post(
            f"{AI_BASE_URL}/images/generations",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0].get("url")
        else:
            print(f"Image API error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Image generation error: {e}")
    return None

def check_image_request(text: str) -> bool:
    """Проверяет, просит ли пользователь изображение."""
    if not text:
        return False
    text_lower = text.lower()
    image_keywords = [
        "нарисуй", "картинку", "изображение", "сгенерируй", "рисуй", "покажи",
        "draw", "image", "picture", "create", "generate", "show me"
    ]
    return any(keyword in text_lower for keyword in image_keywords)

def get_system_prompt(agent_type: str, description: str) -> str:
    """Получить системный промпт для агента."""
    if description and description.strip():
        if agent_type in SYSTEM_PROMPTS:
            return f"{SYSTEM_PROMPTS[agent_type]}\n\nДополнительная специализация: {description}"
        return description
    return SYSTEM_PROMPTS.get(agent_type, "Ты — полезный ИИ ассистент. Помогай пользователю по его запросам.")

def _detect_language(text: str) -> str:
    """Примитивный детектор языка по unicode/ключевым словам."""
    t = (text or "").strip()

    if not t:
        return "ru"


    # Китайский: базовая эвристика по диапазонам CJK
    if any("\u4e00" <= ch <= "\u9fff" for ch in t):
        return "zh"

    lower = t.lower()
    # Русский/украинский: кириллица
    if any("а" <= ch.lower() <= "я" for ch in t if ch.isalpha()):
        return "ru"

    # Испанский ключевые слова (минимально)
    es_markers = ["como", "gracias", "por favor", "que", "por qué"]
    if any(m in lower for m in es_markers):
        return "es"

    # Английский по умолчанию для латиницы
    return "en"


def _detect_expert_mode(text: str) -> bool:
    t = (text or "").lower()
    expert_markers = ["expert", "эксперт", "подробно", "углуб", "deep dive", "подробный", "с примерами", "с источниками"]
    return any(m in t for m in expert_markers)


def _detect_complexity(text: str) -> str:
    """Возвращает: simple|complex"""
    t = (text or "").strip()
    if not t:
        return "simple"
    # Длинные задачи и/или «как автоматизировать/без программирования» => complex
    complex_markers = ["как", "автоматиз", "workflow", "процесс", "без программирован", "без программировани", "интеграц", "сложн", "нестандарт"]
    if len(t) > 250:
        return "complex"
    lower = t.lower()
    if any(m in lower for m in complex_markers):
        return "complex"
    return "simple"


def _language_instruction(lang: str) -> str:
    return {
        "ru": "Отвечай на русском языке.",
        "en": "Answer in English.",
        "es": "Responde en español.",
        "zh": "用中文回答。",
    }.get(lang, "Отвечай на русском языке.")


def generate_ai_response(
    agent_type: str,
    user_message: str,
    description: str = "",
    context: List[Dict] = None,
) -> str:
    """Генерация ответа: сначала пробуем реальный ИИ, если нет — fallback."""
    lang = _detect_language(user_message)
    expert_mode = _detect_expert_mode(user_message)
    complexity = _detect_complexity(user_message)

    system_prompt = get_system_prompt(agent_type, description)

    # Блок экспертности/языка добавляем прямо в system prompt
    system_prompt += "\n\n" + _language_instruction(lang)
    if expert_mode:
        system_prompt += (
            "\nРежим: ЭКСПЕРТ. Дай углублённый ответ: определения, подход, шаги, примеры, trade-offs/риски, краткие ссылки на документацию/источники (можно без точных ссылок, но укажи направления)."
        )
    if complexity == "complex" and agent_type in {"ceo", "researcher", "analyst", "coder"}:
        system_prompt += "\n\nДля сложных задач предложи несколько стратегий/вариантов и объясни, когда какой вариант лучше."


    # Пробуем реальный ИИ
    if AI_API_KEY:
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            for msg in context[-10:]:
                role = "user" if msg.get("sender") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("text", "")})
        messages.append({"role": "user", "content": user_message})
        result = call_real_ai(messages)
        if result:
            return result

    # === FALLBACK: умные шаблоны ===
    msg_lower = user_message.lower()

    greetings = ["привет", "здравствуй", "hello", "hi", "доброго", "ку", "хай"]
    if any(g in msg_lower for g in greetings):
        return (
            f"Привет! Я {agent_type.upper()}.\n\n"
            f"Моя роль: {description or SYSTEM_PROMPTS.get(agent_type, 'помогать вам')}\n\n"
            f"Чем могу помочь?"
        )

    task_words = ["нужно", "надо", "задача", "сделай", "напиши", "создай", "подготовь", "выполни", "помоги"]
    if any(w in msg_lower for w in task_words):
        return (
            f"✅ Задача принята!\n\n"
            f"📝 {user_message}\n\n"
            f"👉 Я приступаю к выполнению как {agent_type.upper()}.\n"
            f"🔄 Статус: В работе\n\n"
            f"💡 *Примечание: для получения развёрнутого ИИ-ответа подключите API-ключ в .env*"
        )

    code_words = ["код", "python", "javascript", "sql", "программ", "скрипт", "функция"]
    if any(w in msg_lower for w in code_words):
        return (
            f"💻 Вот базовый шаблон:\n\n"
            f"```python\n"
            f"# TODO: реализация для задачи\n"
            f"def solve():\n"
            f"    pass\n"
            f"```\n\n"
            f"Для полноценного кода подключите ИИ API в настройках."
        )

    return (
        f"Я понял ваш запрос: *{user_message}*\n\n"
        f"Как {agent_type.upper()}, я готов помочь. "
        f"Для более умных ответов подключите API-ключ (OpenRouter, Groq и т.д.) в файл .env"
    )

# === PYDANTIC MODELS ===
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class AgentCreate(BaseModel):
    name: str
    agent_type: str = Field(default="custom", description="Тип агента или 'custom' для кастомного")
    description: str = ""
    user_id: int

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SocialPost(BaseModel):
    agent_id: int
    user_id: int
    platform: str  # "tg" или "vk"
    text: str
    chat_id: Optional[str] = None  # для TG

class TaskCreate(BaseModel):
    title: str
    description: str
    agent_id: Optional[int] = None  # по умолчанию CEO распределит задачу
    user_id: int

class TaskExecute(BaseModel):
    user_id: int

class MessageCreate(BaseModel):
    agent_id: int
    user_id: int
    text: str
    sender: str
    image: Optional[str] = None

# === ROUTES ===
@app.get("/")
async def root():
    return {"message": "AI Agents Manager API v3.0", "status": "running", "ai_enabled": bool(AI_API_KEY)}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "ai_enabled": bool(AI_API_KEY)}

# --- AUTH ---
@app.post("/api/v1/auth/register")
async def register(user: UserCreate):
    users = load_json(USERS_FILE, [])
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    new_user = {
        "id": now_ms(),
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "reg_date": datetime.now().isoformat(),
        "visit_count": 0,
    }
    users.append(new_user)
    save_json(USERS_FILE, users)
    return {"message": "Регистрация успешна", "user": {"id": new_user["id"], "name": new_user["name"], "email": new_user["email"]}}

@app.post("/api/v1/auth/login")
async def login(user: UserLogin):
    users = load_json(USERS_FILE, [])
    hashed = hash_password(user.password)
    found_user = next((u for u in users if u["email"] == user.email and u["password"] == hashed), None)

    if not found_user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    found_user["visit_count"] = found_user.get("visit_count", 0) + 1
    save_json(USERS_FILE, users)

    return {
        "message": "Вход успешен",
        "user": {
            "id": found_user["id"],
            "name": found_user["name"],
            "email": found_user["email"],
            "reg_date": found_user["reg_date"],
        },
    }

# --- AGENTS ---
@app.get("/api/v1/agents/{user_id}")
async def get_agents(user_id: int):
    agents = load_json(AGENTS_FILE, [])
    user_agents = [a for a in agents if a.get("user_id") == user_id]
    if not user_agents:
        default_agents = [
            {"id": now_ms(), "user_id": user_id, "name": "Ген Директор", "agent_type": "ceo", "is_active": True, "description": "Главный агент, управляет командой"},
            {"id": now_ms() + 1, "user_id": user_id, "name": "Программист", "agent_type": "coder", "is_active": True, "description": "Пишет код на Python, JavaScript, SQL"},
            {"id": now_ms() + 2, "user_id": user_id, "name": "Исследователь", "agent_type": "researcher", "is_active": True, "description": "Ищет и анализирует информацию"},
        ]
        agents.extend(default_agents)
        save_json(AGENTS_FILE, agents)
        user_agents = default_agents
    return user_agents

@app.post("/api/v1/agents")
async def create_agent(agent: AgentCreate):
    agents = load_json(AGENTS_FILE, [])
    new_agent = {
        "id": now_ms(),
        "user_id": agent.user_id,
        "name": agent.name,
        "agent_type": agent.agent_type,
        "description": agent.description,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
    }
    agents.append(new_agent)
    save_json(AGENTS_FILE, agents)
    return {"message": "Агент создан", "agent": new_agent}

@app.delete("/api/v1/agents/{agent_id}")
async def delete_agent(agent_id: int, user_id: int):
    agents = load_json(AGENTS_FILE, [])
    agent = next((a for a in agents if a["id"] == agent_id and a.get("user_id") == user_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")

    agents = [a for a in agents if not (a["id"] == agent_id and a.get("user_id") == user_id)]
    save_json(AGENTS_FILE, agents)

    tasks = load_json(TASKS_FILE, [])
    tasks = [t for t in tasks if t.get("agent_id") != agent_id]
    save_json(TASKS_FILE, tasks)

    messages = load_json(MESSAGES_FILE, [])
    messages = [m for m in messages if m.get("agent_id") != agent_id]
    save_json(MESSAGES_FILE, messages)

    return {"message": "Агент удалён"}

@app.put("/api/v1/agents/{agent_id}")
async def update_agent(agent_id: int, user_id: int, update: AgentUpdate):
    agents = load_json(AGENTS_FILE, [])
    agent = next((a for a in agents if a["id"] == agent_id and a.get("user_id") == user_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")

    if update.name is not None:
        agent["name"] = update.name
    if update.description is not None:
        agent["description"] = update.description
    if update.is_active is not None:
        agent["is_active"] = update.is_active

    save_json(AGENTS_FILE, agents)
    return {"message": "Агент обновлён", "agent": agent}

# --- MESSAGES ---
@app.post("/api/v1/messages")
async def send_message(msg: MessageCreate):
    agents = load_json(AGENTS_FILE, [])
    agent = next((a for a in agents if a["id"] == msg.agent_id and a.get("user_id") == msg.user_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")

    messages = load_json(MESSAGES_FILE, [])
    context = [m for m in messages if m["agent_id"] == msg.agent_id and m["user_id"] == msg.user_id][-20:]

    # Проверяем, просит ли пользователь изображение
    image_url = None
    if AI_API_KEY and check_image_request(msg.text):
        image_url = generate_image(msg.text)
        if image_url:
            print(f"✅ Image generated for user {msg.user_id}")

    ai_response = generate_ai_response(
        agent.get("agent_type", "custom"),
        msg.text,
        agent.get("description", ""),
        context,
    )

    user_msg = {
        "id": now_ms(),
        "agent_id": msg.agent_id,
        "user_id": msg.user_id,
        "text": msg.text,
        "sender": "user",
        "timestamp": datetime.now().isoformat(),
        "image": None,
    }
    ai_msg = {
        "id": now_ms() + 1,
        "agent_id": msg.agent_id,
        "user_id": msg.user_id,
        "text": ai_response,
        "sender": "agent",
        "timestamp": datetime.now().isoformat(),
        "image": image_url,
    }
    messages.extend([user_msg, ai_msg])
    save_json(MESSAGES_FILE, messages)

    return {"message": "Сообщения отправлены", "response": ai_response, "image": image_url}

@app.get("/api/v1/messages/{agent_id}/{user_id}")
async def get_messages(agent_id: int, user_id: int):
    messages = load_json(MESSAGES_FILE, [])
    return [m for m in messages if m["agent_id"] == agent_id and m["user_id"] == user_id]

# --- TASKS ---

def _append_task_log(task: dict, line: str):
    # 1 строка для UI
    if task.get("process_line") is None:
        task["process_line"] = ""
    if task["process_line"]:
        task["process_line"] += " | "
    task["process_line"] += line

    # массив шагов
    if task.get("progress_log") is None:
        task["progress_log"] = []
    task["progress_log"].append({
        "ts": datetime.now().isoformat(),
        "line": line,
    })

    return task


def _pick_ceo_agent(agents: list, user_id: int):
    ceo = next((a for a in agents if a.get("user_id") == user_id and a.get("agent_type") == "ceo" and a.get("is_active")), None)
    if ceo:
        return ceo
    return next((a for a in agents if a.get("user_id") == user_id and a.get("is_active")), None)


@app.post("/api/v1/tasks")
async def create_task(task: TaskCreate):
    tasks = load_json(TASKS_FILE, [])
    new_task = {
        "id": now_ms(),
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "agent_id": task.agent_id,
        "status": "pending",
        "result": None,
        "process_line": "",
        "progress_log": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    tasks.append(new_task)
    save_json(TASKS_FILE, tasks)
    return {"message": "Задача создана", "task": new_task}


@app.post("/api/v1/tasks/{task_id}/execute")
async def execute_task(task_id: int, body: TaskExecute):
    # Временно оставляем старый single-agent endpoint для обратной совместимости.
    # CEO workflow добавлен отдельным endpoint execute_v2.
    pass
    tasks = load_json(TASKS_FILE, [])
    task = next((t for t in tasks if t["id"] == task_id and t.get("user_id") == body.user_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    agents = load_json(AGENTS_FILE, [])
    agent = next((a for a in agents if a["id"] == task["agent_id"]), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент задачи не найден")

    prompt = (
        f"Ты получил задачу от пользователя.\n\n"
        f"Название: {task['title']}\n"
        f"Описание: {task['description']}\n\n"
        f"Выполни эту задачу максимально качественно. Если это код — напиши рабочий код. "
        f"Если это анализ — дай развёрнутый ответ с выводами. "
        f"Если это текст — напиши готовый к использованию материал."
    )

    result = generate_ai_response(
        agent.get("agent_type", "custom"),
        prompt,
        agent.get("description", ""),
    )

    task["status"] = "completed"
    task["result"] = result
    task["completed_at"] = datetime.now().isoformat()
    save_json(TASKS_FILE, tasks)

    return {"message": "Задача выполнена", "task": task}

@app.post("/api/v1/tasks/{task_id}/execute_v2")
async def execute_task_v2(task_id: int, body: TaskExecute):
    tasks = load_json(TASKS_FILE, [])
    task = next((t for t in tasks if t["id"] == task_id and t.get("user_id") == body.user_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.get("status") not in ["pending", "failed", None]:
        return {"message": "Задача уже выполнялась", "task": task}

    agents = load_json(AGENTS_FILE, [])
    ceo = _pick_ceo_agent(agents, body.user_id)
    if not ceo:
        raise HTTPException(status_code=404, detail="CEO агент не найден")

    task["status"] = "running"
    task.setdefault("progress_log", [])
    task.setdefault("process_line", "")
    _append_task_log(task, "CEO: задача принята")
    save_json(TASKS_FILE, tasks)

    plan_prompt = (
        "Ты — Генеральный директор ИИ-компании.\n"
        "Разбей задачу пользователя на подзадачи по ролям агентов: coder, researcher, analyst, poster.\n"
        "Верни ТОЛЬКО JSON в формате:\n"
        "{\n"
        '  "steps": [\n'
        '    {"agent_type": "coder|researcher|analyst|poster", "action": "..."}\n'
        '  ],\n'
        '  "final_action": "..."\n'
        "}\n\n"
        f"Задача: {task['title']}\n{task['description']}"
    )

    plan_text = generate_ai_response(
        ceo.get("agent_type", "ceo"),
        plan_prompt,
        ceo.get("description", ""),
        context=None,
    )

    steps = []
    try:
        import re
        import json as _json
        m = re.search(r"\{[\s\S]*\}", plan_text or "")
        raw = m.group(0) if m else (plan_text or "")
        parsed = _json.loads(raw)
        steps = parsed.get("steps", [])
    except Exception:
        steps = [{"agent_type": "coder", "action": "выполни задачу"}]

    result_parts = []

    for idx, st in enumerate(steps, start=1):
        agent_type = st.get("agent_type")
        action = st.get("action", "")

        step_agent = next(
            (a for a in agents if a.get("user_id") == body.user_id and a.get("agent_type") == agent_type and a.get("is_active")),
            None,
        )
        if not step_agent:
            _append_task_log(task, f"Шаг {idx}: нет агента {agent_type}, пропуск")
            continue

        _append_task_log(task, f"Шаг {idx}: {agent_type} — {action[:60]}")

        step_prompt = (
            f"Ты агент роли: {agent_type}.\n"
            f"Подзадача: {action}\n\n"
            f"Исходная задача пользователя: {task['title']}\n{task['description']}\n"
        )

        step_text = generate_ai_response(
            step_agent.get("agent_type", "custom"),
            step_prompt,
            step_agent.get("description", ""),
            context=None,
        )

        result_parts.append(f"[{agent_type}]\n{step_text}")
        save_json(TASKS_FILE, tasks)

    _append_task_log(task, "CEO: агрегирование результата")
    final_prompt = (
        "Ты CEO. Сформируй финальный ответ пользователю на основе результатов агентов.\n"
        f"Задача: {task['title']}\n{task['description']}\n\n"
        f"Результаты:\n{'\n'.join(result_parts)}\n"
    )

    final_result = generate_ai_response(
        ceo.get("agent_type", "ceo"),
        final_prompt,
        ceo.get("description", ""),
        context=None,
    )

    task["status"] = "completed"
    task["result"] = final_result
    task["completed_at"] = datetime.now().isoformat()
    _append_task_log(task, "CEO: готово")

    save_json(TASKS_FILE, tasks)
    return {"message": "Задача выполнена", "task": task}


@app.get("/api/v1/tasks/{user_id}")
async def get_tasks(user_id: int):
    tasks = load_json(TASKS_FILE, [])
    return [t for t in tasks if t["user_id"] == user_id]

# --- ADMIN ---
@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    users = load_json(USERS_FILE, [])
    agents = load_json(AGENTS_FILE, [])
    visits = load_json(VISITS_FILE, [])
    today = datetime.now().date().isoformat()[:10]

    return {
        "total_users": len(users),
        "total_agents": len(agents),
        "total_visits": len(visits),
        "today_visits": len([v for v in visits if v.get("date", "")[:10] == today]),
        "ai_enabled": bool(AI_API_KEY),
        "ai_model": AI_MODEL if AI_API_KEY else None,
    }

@app.post("/api/v1/admin/track-visit")
async def track_visit():
    visits = load_json(VISITS_FILE, [])
    visits.append({"date": datetime.now().isoformat(), "timestamp": datetime.now().timestamp()})
    save_json(VISITS_FILE, visits)
    return {"message": "Посещение записано"}

# --- AI STATUS ---
@app.get("/api/v1/ai/status")
async def ai_status():
    return {
        "enabled": bool(AI_API_KEY),
        "model": AI_MODEL,
        "base_url": AI_BASE_URL,
    }

# === STATIC FILES (frontend) ===
# Раздаём frontend так, чтобы ссылки вида /dashboard.html и /js/auth.js работали.
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
