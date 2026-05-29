"""
Telegram и VK интеграция для AI Agents Manager
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import json
import requests
from typing import Optional, Dict, Any

app = FastAPI(title="Social Media Integration", version="1.0.0")

# === CONFIG ===
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
VK_GROUP_ID = os.getenv("VK_GROUP_ID", "")
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN", "")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
TG_WEBHOOK_FILE = os.path.join(DATA_DIR, "tg_webhook.json")
VK_WEBHOOK_FILE = os.path.join(DATA_DIR, "vk_webhook.json")

def load_json(filepath: str, default: Any = None):
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Load JSON error: {e}")
    return default

def save_json(filepath: str, data: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === TELEGRAM ===
@app.post("/api/v1/social/tg/webhook/{bot_token}")
async def tg_webhook(bot_token: str, request: Request):
    """Вебхук для Telegram бота"""
    if bot_token != TG_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    body = await request.json()
    print(f"TG Update: {json.dumps(body, ensure_ascii=False)[:200]}")
    
    # Здесь можно добавить обработку сообщений
    # Для примера — просто логируем
    tg_updates = load_json(TG_WEBHOOK_FILE, [])
    tg_updates.append({
        "update": body,
        "timestamp": body.get("update_id", 0)
    })
    save_json(TG_WEBHOOK_FILE, tg_updates[-100:])  # Хранить последние 100
    
    return {"ok": True}

@app.post("/api/v1/social/tg/send")
async def tg_send_message(chat_id: str, text: str):
    """Отправить сообщение в Telegram"""
    if not TG_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="TG_BOT_TOKEN not configured")
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        if resp.status_code == 200:
            return {"ok": True, "response": resp.json()}
        else:
            raise HTTPException(status_code=400, detail=f"TG API error: {resp.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/tg/post")
async def tg_post_to_channel(channel_username: str, text: str):
    """Опубликовать пост в Telegram канал"""
    if not TG_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="TG_BOT_TOKEN not configured")
    
    # Убираем @ если есть
    channel = channel_username.lstrip("@")
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": f"@{channel}", "text": text, "parse_mode": "Markdown"}, timeout=10)
        if resp.status_code == 200:
            return {"ok": True, "post_id": resp.json().get("message_id")}
        else:
            raise HTTPException(status_code=400, detail=f"TG API error: {resp.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/social/tg/setwebhook")
async def tg_set_webhook(webhook_url: str):
    """Установить webhook для Telegram бота"""
    if not TG_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="TG_BOT_TOKEN not configured")
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/setWebhook"
    try:
        resp = requests.get(f"{url}?url={webhook_url}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise HTTPException(status_code=400, detail=f"TG API error: {resp.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === VK ===
@app.post("/api/v1/social/vk/webhook")
async def vk_webhook(request: Request):
    """Вебхук для VK группы (Confirmation URL)"""
    body = await request.json()
    
    # Подтверждение webhook
    if body.get("type") == "confirmation":
        return VK_GROUP_ID
    
    # Обработка событий
    vk_events = load_json(VK_WEBHOOK_FILE, [])
    vk_events.append({
        "type": body.get("type"),
        "data": body,
        "timestamp": body.get("object", {}).get("date", 0)
    })
    save_json(VK_WEBHOOK_FILE, vk_events[-100:])
    
    return {"ok": True}

@app.post("/api/v1/social/vk/post")
async def vk_post_to_group(text: str, attachments: str = ""):
    """Опубликовать пост в VK группу"""
    if not VK_ACCESS_TOKEN or not VK_GROUP_ID:
        raise HTTPException(status_code=400, detail="VK_ACCESS_TOKEN or VK_GROUP_ID not configured")
    
    url = "https://api.vk.com/method/wall.post"
    try:
        params = {
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131",
            "owner_id": -int(VK_GROUP_ID),  # Минус для групп
            "message": text,
            "attachments": attachments,
            "from_group": 1
        }
        resp = requests.post(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("response"):
                return {"ok": True, "post_id": data["response"].get("post_id")}
            else:
                raise HTTPException(status_code=400, detail=f"VK API error: {data}")
        else:
            raise HTTPException(status_code=400, detail=f"VK HTTP error: {resp.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/vk/comment")
async def vk_comment(post_owner_id: int, post_id: int, text: str):
    """Оставить комментарий к посту VK"""
    if not VK_ACCESS_TOKEN:
        raise HTTPException(status_code=400, detail="VK_ACCESS_TOKEN not configured")
    
    url = "https://api.vk.com/method/wall.createComment"
    try:
        params = {
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131",
            "owner_id": post_owner_id,
            "post_id": post_id,
            "message": text,
            "from_group": 1
        }
        resp = requests.post(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("response"):
                return {"ok": True, "comment_id": data["response"].get("comment_id")}
            else:
                raise HTTPException(status_code=400, detail=f"VK API error: {data}")
        else:
            raise HTTPException(status_code=400, detail=f"VK HTTP error: {resp.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/vk/send_message")
async def vk_send_message(user_id: int, text: str):
    """Отправить сообщение пользователю VK (Messages API)"""
    if not VK_ACCESS_TOKEN:
        raise HTTPException(status_code=400, detail="VK_ACCESS_TOKEN not configured")
    
    url = "https://api.vk.com/method/messages.send"
    try:
        params = {
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131",
            "user_id": user_id,
            "message": text
        }
        resp = requests.post(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("response"):
                return {"ok": True, "message_id": data["response"]}
            else:
                raise HTTPException(status_code=400, detail=f"VK API error: {data}")
        else:
            raise HTTPException(status_code=400, detail=f"VK HTTP error: {resp.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === STATUS ===
@app.get("/api/v1/social/status")
async def social_status():
    """Статус подключений"""
    return {
        "telegram": bool(TG_BOT_TOKEN),
        "vk": bool(VK_ACCESS_TOKEN and VK_GROUP_ID),
        "tg_webhook_url": os.getenv("TG_WEBHOOK_URL", "Not set")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
