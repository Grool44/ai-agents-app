"""
Telegram Client API (MTProto) — настоящий аккаунт, а не бот
Агент может писать первым, выглядит как человек
"""
import os
import asyncio
import json
from typing import Dict, Optional

# Telethon используется только для Telegram MTProto-операций.
# Чтобы сервер (и кнопки сайта) могли работать даже без telethon,
# импорт делаем опциональным.
try:
    from telethon import TelegramClient, events  # type: ignore
    from telethon.sessions import StringSession  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    TelegramClient = None  # type: ignore
    events = None  # type: ignore
    StringSession = None  # type: ignore


# === CONFIG ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

TELEGRAM_SESSIONS_DIR = os.path.join(DATA_DIR, "tg_sessions")
os.makedirs(TELEGRAM_SESSIONS_DIR, exist_ok=True)

# Получите эти ключи на https://my.telegram.org
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY", "")  # Например: socks5://user:pass@host:1080

# Хранилище активных клиентов
clients: Dict[int, TelegramClient] = {} if TelegramClient else {} 


class TelegramUserClient:
    """Клиент для работы с Telegram как с обычным аккаунтом"""

    def __init__(self, agent_id: int, user_id: int, phone: str, api_id: str, api_hash: str):
        self.agent_id = agent_id
        self.user_id = user_id
        self.phone = phone
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_path = os.path.join(TELEGRAM_SESSIONS_DIR, f"{user_id}_{agent_id}")
        self.client: Optional[TelegramClient] = None
        self.is_logged = False
        self.proxy = TELEGRAM_PROXY if TELEGRAM_PROXY else None
    
    def _check_credentials(self):
        if not self.api_id or not self.api_hash:
            return {"status": "error", "message": "TELEGRAM_API_ID и TELEGRAM_API_HASH не настроены в .env"}
        try:
            int(self.api_id)
        except ValueError:
            return {"status": "error", "message": "TELEGRAM_API_ID должен быть числом"}
        return None

    def _create_client(self):
        """Создать TelegramClient с файловой сессией"""
        kwargs = {}
        if self.proxy:
            kwargs["proxy"] = self.proxy
        return TelegramClient(self.session_path, int(self.api_id), self.api_hash, **kwargs)

    async def login(self):
        """Вход в Telegram по номеру телефона"""
        if not TelegramClient:
            return {"status": "error", "message": "telethon не установлен. pip install telethon"}
        err = self._check_credentials()
        if err:
            return err

        self.client = self._create_client()
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            return {"status": "code_sent", "message": "Код отправлен на телефон"}
        else:
            self.is_logged = True
            return {"status": "already_logged", "message": "Уже авторизован"}

    async def login_with_code(self, code: str):
        """Ввод кода из SMS"""
        if not self.client:
            return {"status": "error", "message": "Клиент Telegram не инициализирован"}
        try:
            await self.client.sign_in(self.phone, code)
            # Сохраняем сессию
            if self.client.session:
                self.client.session.save()
            self.is_logged = True
            return {"status": "success", "message": "Успешная авторизация"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def start_session(self):
        """Запустить сессию (уже авторизованного пользователя)"""
        err = self._check_credentials()
        if err:
            return err
        self.client = self._create_client()
        await self.client.connect()

        if await self.client.is_user_authorized():
            self.is_logged = True
            return {"status": "success", "me": await self.client.get_me()}
        return {"status": "not_authorized"}
    
    async def send_message(self, target: str, message: str):
        """Отправить сообщение пользователю/чату/каналу"""
        if not self.client or not self.is_logged:
            return {"ok": False, "error": "Не авторизован. Выполните login + login_with_code"}

        try:
            entity = await self.client.get_entity(target)
            await self.client.send_message(entity, message)
            return {"ok": True, "message": "Сообщение отправлено"}
        except Exception as e:
            return {"ok": False, "error": f"Ошибка отправки: {str(e)}"}

    async def send_to_channel(self, channel_username: str, message: str):
        """Опубликовать пост в канал/группу"""
        if not self.client or not self.is_logged:
            return {"ok": False, "error": "Не авторизован"}
        
        try:
            channel = channel_username.lstrip("@")
            entity = await self.client.get_entity(f"@{channel}")
            await self.client.send_message(entity, message)
            return {"ok": True, "message": "Пост опубликован"}
        except Exception as e:
            return {"ok": False, "error": f"Ошибка публикации: {str(e)}"}
    
    async def get_me(self):
        """Получить информацию о себе"""
        if not self.client or not self.is_logged:
            return None
        try:
            return await self.client.get_me()
        except:
            return None
    
    async def disconnect(self):
        """Отключиться"""
        if self.client:
            await self.client.disconnect()
            self.is_logged = False

# === ГЛОБАЛЬНЫЕ КЛИЕНТЫ ===
active_clients: Dict[int, TelegramUserClient] = {}

async def get_or_create_client(agent_id: int, user_id: int, phone: str) -> TelegramUserClient:
    """Получить или создать клиента для агента."""
    key = agent_id
    if key not in active_clients:
        client = TelegramUserClient(agent_id, user_id, phone, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        active_clients[key] = client
        # Пробуем восстановить сессию из файла
        await client.start_session()
    else:
        existing_client = active_clients[key]
        if not existing_client.is_logged:
            await existing_client.start_session()
    return active_clients[key]



async def start_client_session(agent_id: int):
    """Запустить сессию для агента"""
    if agent_id in active_clients:
        return await active_clients[agent_id].start_session()
    return {"status": "error", "message": "Клиент не найден"}

async def send_telegram_message(agent_id: int, target: str, message: str):
    """Отправить сообщение через агента (MTProto).

    Если сервер перезапущен и клиент не поднят в памяти — вернём понятную ошибку.
    """
    if agent_id not in active_clients:
        return {
            "ok": False,
            "error": "Клиент не найден в памяти. Выполните tg/login + tg/verify для этого agent_id ещё раз (после рестарта сервера).",
        }

    return await active_clients[agent_id].send_message(target, message)


async def send_to_telegram_channel(agent_id: int, channel: str, message: str):
    """Опубликовать в канал"""
    if agent_id not in active_clients:
        return {"ok": False, "error": "Клиент не найден"}
    return await active_clients[agent_id].send_to_channel(channel, message)
