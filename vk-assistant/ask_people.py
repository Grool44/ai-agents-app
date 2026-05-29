"""
Автоматический опрос людей.
Запуск: py ask_people.py
"""
from config import VK_USER_TOKEN
from vk_client import VkAssistant


def ask_people(bot: VkAssistant, user_ids: list, question: str):
    """
    Отправляет вопрос списку людей.
    user_ids: список ID пользователей [123, 456, 789]
    question: текст вопроса
    """
    print(f"\n=== ОПРОС {len(user_ids)} человек ===")
    print(f"Вопрос: {question}\n")
    
    for user_id in user_ids:
        print(f"[{user_id}] Отправляю вопрос...", end=" ")
        result = bot.send_message(user_id, question)
        
        if result:
            print("OK")
        else:
            print("ERROR")
        
        import time
        time.sleep(1.5)  # Лимиты API
    
    print(f"\nОпрос отправлен {len(user_ids)} людям!")


def main():
    bot = VkAssistant(token=VK_USER_TOKEN)
    
    # ========================================
    # НАСТРОЙКА: укажи ID людей и вопрос
    # ========================================
    
    # Пример: ID из твоих диалогов
    target_users = [
        701427696,  # <-- вставь сюда ID
        89790613,   # <-- вставь сюда ID
        # 123456789,  # добавляй новые через запятую
    ]
    
    question = """Привет!
    
У меня есть вопрос к тебе. Можешь ответить, пожалуйста?

(напиши свой ответ)"""
    
    # ========================================
    
    print("Получатели:", target_users)
    print("\nВопрос:")
    print(question)
    print("\nНажми Enter для отправки или Ctrl+C для отмены...")
    input()
    
    ask_people(bot, target_users, question)


if __name__ == "__main__":
    main()
