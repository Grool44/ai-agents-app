"""
Отправка сообщений по списку.
Запуск: py send_messages.py 701427696,89790613
Запуск интерактивный: py send_messages.py --interactive
"""
import sys
import argparse
from config import VK_USER_TOKEN
from vk_client import VkAssistant


def send_to_users(bot: VkAssistant, user_ids: list, message: str, delay: float = 1.0):
    """Отправляет сообщение списку пользователей."""
    import time
    
    print(f"\nОтправка {len(user_ids)} сообщений...")
    print(f"Сообщение: {message[:50]}...\n")
    
    results = {"success": 0, "failed": 0}
    
    for user_id in user_ids:
        print(f"   -> ID {user_id}...", end=" ")
        result = bot.send_message(user_id, message)
        
        if result:
            results["success"] += 1
            print("OK")
        else:
            results["failed"] += 1
            print("ERROR")
        
        time.sleep(delay)  # Лимиты API
    
    print(f"\nИтого: {results['success']} успешно, {results['failed']} ошибок")
    return results


def main():
    parser = argparse.ArgumentParser(description="Отправка сообщений VK")
    parser.add_argument("user_ids", nargs="?", help="ID пользователей через запятую: 123,456,789")
    parser.add_argument("--interactive", "-i", action="store_true", help="Интерактивный режим")
    parser.add_argument("--message", "-m", default="", help="Текст сообщения")
    parser.add_argument("--delay", "-d", type=float, default=1.5, help="Задержка между сообщениями (сек)")
    
    args = parser.parse_args()
    
    bot = VkAssistant(token=VK_USER_TOKEN)
    
    if args.interactive:
        # Интерактивный режим
        print("\n=== ИНТЕРАКТИВНЫЙ РЕЖИМ ===")
        print("\nПолучатели (ID через запятую):")
        user_ids_str = input(">>> ").strip()
        user_ids = [int(x.strip()) for x in user_ids_str.split(",") if x.strip()]
        
        print("\nСообщение:")
        message = input(">>> ").strip()
        
        if not user_ids or not message:
            print("ОШИБКА: нужны ID и текст сообщения")
            return
        
        send_to_users(bot, user_ids, message, args.delay)
    
    elif args.user_ids:
        # Режим командной строки
        user_ids = [int(x.strip()) for x in args.user_ids.split(",") if x.strip()]
        
        if not args.message:
            print("ОШИБКА: укажите текст сообщения через --message")
            print("Пример: py send_messages.py 123,456 -m 'Привет!'")
            return
        
        send_to_users(bot, user_ids, args.message, args.delay)
    
    else:
        print("Используй --interactive или укажи ID и сообщение")
        print("Примеры:")
        print("  py send_messages.py --interactive")
        print("  py send_messages.py 123,456 -m 'Привет!'")


if __name__ == "__main__":
    main()
