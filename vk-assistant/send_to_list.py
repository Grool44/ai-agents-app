"""
Отправка сообщения списку людей.
Запуск: py send_to_list.py
"""
from config import VK_USER_TOKEN
from vk_client import VkAssistant


def main():
    bot = VkAssistant(token=VK_USER_TOKEN)
    
    print("=" * 50)
    print("ОТПРАВКА СООБЩЕНИЙ СПИСКУ ЛЮДЕЙ")
    print("=" * 50)
    
    # 1. Ввод ID получателей
    print("\nВведи ID получателей через запятую:")
    print("Пример: 123456, 789012, @durov")
    ids_input = input("ID: ").strip()
    
    # Парсим ID
    raw_ids = [x.strip() for x in ids_input.split(",")]
    user_ids = []
    
    for raw in raw_ids:
        if raw.startswith("@"):
            # Ищем по short-нику
            search_q = raw[1:]
            resp = bot.vk.users.search(q=search_q, count=1)
            if resp.get("items"):
                uid = resp["items"][0]["id"]
                user_ids.append(uid)
                print(f"  {raw} -> id{uid}")
            else:
                print(f"  {raw}: не найден")
        elif raw.isdigit():
            user_ids.append(int(raw))
        else:
            print(f"  {raw}: не распознан")
    
    if not user_ids:
        print("\nНикого не нашёл. Попробуй снова.")
        return
    
    # 2. Ввод сообщения
    print("\nВведи сообщение (можно многострочное, нажмите Enter дважды для завершения):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    message = "\n".join(lines)
    
    if not message:
        print("Сообщение пустое. Попробуй снова.")
        return
    
    # 3. Подтверждение
    print(f"\nБудет отправлено {len(user_ids)} сообщений:")
    for uid in user_ids:
        print(f"  - id{uid}")
    print(f"\nСообщение:\n{message}\n")
    
    confirm = input("Отправить? (да/нет): ").strip().lower()
    if confirm not in ["да", "д", "y", "yes"]:
        print("Отменено")
        return
    
    # 4. Отправка
    print("\n" + "=" * 50)
    print("ОТПРАВКА...")
    print("=" * 50)
    
    success = 0
    failed = 0
    
    for uid in user_ids:
        result = bot.send_message(uid, message)
        if result:
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"ГОТОВО: Успешно {success}, Ошибок {failed}")
    print("=" * 50)


if __name__ == "__main__":
    main()
