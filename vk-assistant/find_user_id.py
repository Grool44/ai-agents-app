"""
Поиск ID пользователей по никнейму или имени.
Запуск: py find_user_id.py durov
"""
import sys
from config import VK_USER_TOKEN
from vk_client import VkAssistant


def find_user(bot: VkAssistant, query: str):
    """Ищет пользователя по имени или short-нику."""
    print(f"\nПоиск: {query}")
    
    # По short-нику (vk.com/durov)
    try:
        if not query.startswith("@") and not query.startswith("vk.com/"):
            query = f"@{query}"
        
        # Ищем через search
        resp = bot.vk.users.search(q=query.replace("@", ""), count=5)
        users = resp.get("items", [])
        
        if users:
            print(f"\nНайдено {len(users)} пользователей:")
            for i, u in enumerate(users, 1):
                print(f"  {i}. {u['first_name']} {u['last_name']} (id{u['id']})")
                print(f"     vk.com/id{u['id']}")
            return users
        else:
            print("Никого не нашёл")
            return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


def main():
    bot = VkAssistant(token=VK_USER_TOKEN)
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("Поиск (имя или short-ник, напр. durov): ").strip()
    
    find_user(bot, query)


if __name__ == "__main__":
    main()
