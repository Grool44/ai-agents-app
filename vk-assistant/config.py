import os
from dotenv import load_dotenv

load_dotenv()

VK_USER_TOKEN = os.getenv("VK_USER_TOKEN", "")
VK_SERVICE_TOKEN = os.getenv("VK_SERVICE_TOKEN", "")
VK_APP_ID = os.getenv("VK_APP_ID", "")

if not VK_USER_TOKEN:
    raise ValueError(
        "❌ VK_USER_TOKEN не найден!\n"
        "   1. Скопируй .env.example → .env\n"
        "   2. Вставь свой user access token\n"
        "   Получить токен: https://vkhost.github.io/"
    )
