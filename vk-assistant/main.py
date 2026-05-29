"""
VK Ассистент - меню выбора действий.
Запуск: py main.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from config import VK_USER_TOKEN
from vk_client import VkAssistant


def show_menu():
    """Показывает меню и возвращает выбор."""
    print("\n" + "=" * 50)
    print("VK АССИСТЕНТ")
    print("=" * 50)
    print("1. Мои группы")
    print("2. Поиск группы")
    print("3. Диалоги")
    print("4. Отправить сообщение СПИСКУ людей")
    print("5. История с пользователем")
    print("6. Сравнить группы")
    print("7. Сравнить пользователей")
    print("8. Выход")
    print("=" * 50)
    return input("Выбери: ").strip()


def main():
    bot = VkAssistant(token=VK_USER_TOKEN)

    while True:
        choice = show_menu()
        
        if choice == "1":
            groups = bot.get_my_groups(count=10)
            print(f"\n[Группы] Найдено {len(groups)} групп:")
            for g in groups:
                print(f"   • {g['name']} ({g.get('members_count', '?')} подписчиков)")
        
        elif choice == "2":
            q = input("Поиск: ").strip()
            found = bot.search_groups(q, count=5)
            print(f"\n[Поиск] Найдено {len(found)} групп:")
            for g in found:
                print(f"   • {g['name']} (vk.com/{g['screen_name']})")
        
        elif choice == "3":
            convs = bot.get_conversations(count=10)
            print(f"\n[Диалоги] Найдено {len(convs)} диалогов:")
            for item in convs:
                conv = item["conversation"]
                last = item["last_message"]
                peer_id = conv["peer"]["id"]
                text = last.get("text", "")[:40].replace("\n", " ")
                print(f"   [{peer_id}] {text}...")
        
        elif choice == "4":
            # Запуск отправки списку
            import subprocess
            subprocess.run(["py", "send_to_list.py"])
        
        elif choice == "5":
            uid = input("ID пользователя: ").strip()
            if uid.startswith("@"):
                uid = uid[1:]
                resp = bot.vk.users.search(q=uid, count=1)
                if resp.get("items"):
                    uid = resp["items"][0]["id"]
                else:
                    print("Не найден")
                    continue
            history = bot.get_history(int(uid), count=10)
            print(f"\n[История] с id{uid}:")
            for msg in history:
                print(f"   [{msg['date']}] {msg['text'][:60]}")
        
        elif choice == "6":
            ids = input("ID групп через запятую (напр. vk,durov): ").strip()
            groups = ids.split(",")
            result = bot.compare_groups(groups)
            print(f"\n[Сравнение] {len(result)} групп:")
            for g in result:
                print(f"   • {g['name']}: {g['members_count']} подписчиков")
        
        elif choice == "7":
            ids = input("ID пользователей через запятую (напр. 1,2): ").strip()
            user_ids = [int(x) for x in ids.split(",") if x.strip().isdigit()]
            result = bot.compare_users(user_ids)
            print(f"\n[Сравнение] {len(result)} пользователей:")
            for u in result:
                print(f"   • {u['first_name']} {u['last_name']} (id{u['id']})")
        
        elif choice == "8":
            print("Пока!")
            break
        
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()
