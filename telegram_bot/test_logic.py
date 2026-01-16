#!/usr/bin/env python3
"""
Скрипт для тестирования логики бота без реального Telegram API.
Проверяет работу всех функций и логику обработки команд.
"""

import sys
from database import (
    init_db,
    add_user,
    check_user_paid,
    check_materials_sent,
    mark_user_paid,
    mark_materials_sent,
    get_user_info
)

def test_user_flow():
    """Тестирование полного сценария работы пользователя."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЛОГИКИ БОТА")
    print("=" * 60)
    
    # Инициализация БД
    print("\n1. Инициализация базы данных...")
    init_db()
    print("✅ База данных инициализирована")
    
    # Тестовый пользователь
    test_user_id = 999999999
    test_username = "test_user"
    test_first_name = "Тестовый Пользователь"
    
    # Добавление пользователя (симуляция /start)
    print(f"\n2. Симуляция команды /start...")
    add_user(test_user_id, test_username, test_first_name)
    print(f"✅ Пользователь {test_user_id} добавлен")
    
    # Проверка статуса (не оплатил)
    print(f"\n3. Проверка начального статуса...")
    paid = check_user_paid(test_user_id)
    materials = check_materials_sent(test_user_id)
    print(f"   Оплата: {'✅' if paid else '❌'} {paid}")
    print(f"   Материалы: {'✅' if materials else '❌'} {materials}")
    
    if not paid and not materials:
        print("✅ Статус корректный: пользователь не оплатил")
    else:
        print("❌ ОШИБКА: неверный начальный статус")
        sys.exit(1)
    
    # Симуляция кнопки "Оплатить" (первый раз)
    print(f"\n4. Симуляция кнопки '💳 Оплатить' (первый раз)...")
    if not check_user_paid(test_user_id):
        print("   Показаны реквизиты для оплаты")
        print("   Номер карты: 2200 1234 5678 9012")
        print(f"   ID пользователя: `{test_user_id}`")
        print("✅ Реквизиты отображены корректно")
    
    # Администратор отмечает оплату
    print(f"\n5. Администратор отмечает оплату...")
    mark_user_paid(test_user_id)
    print("✅ Пользователь отмечен как оплативший")
    
    # Проверка статуса после оплаты
    print(f"\n6. Проверка статуса после оплаты...")
    paid = check_user_paid(test_user_id)
    materials = check_materials_sent(test_user_id)
    print(f"   Оплата: {'✅' if paid else '❌'} {paid}")
    print(f"   Материалы: {'✅' if materials else '❌'} {materials}")
    
    if paid and not materials:
        print("✅ Статус корректный: оплата получена, материалы в обработке")
    else:
        print("❌ ОШИБКА: неверный статус после оплаты")
        sys.exit(1)
    
    # Симуляция кнопки "Оплатить" (второй раз)
    print(f"\n7. Симуляция кнопки '💳 Оплатить' (повторно)...")
    if check_user_paid(test_user_id):
        print("   Сообщение: 'Вы уже произвели оплату!'")
        print("✅ Повторная оплата заблокирована корректно")
    
    # Администратор отмечает отправку материалов
    print(f"\n8. Администратор отмечает отправку материалов...")
    mark_materials_sent(test_user_id)
    print("✅ Материалы отмечены как отправленные")
    
    # Финальная проверка статуса
    print(f"\n9. Финальная проверка статуса...")
    paid = check_user_paid(test_user_id)
    materials = check_materials_sent(test_user_id)
    print(f"   Оплата: {'✅' if paid else '❌'} {paid}")
    print(f"   Материалы: {'✅' if materials else '❌'} {materials}")
    
    if paid and materials:
        print("✅ Статус корректный: всё завершено")
    else:
        print("❌ ОШИБКА: неверный финальный статус")
        sys.exit(1)
    
    # Получение полной информации о пользователе
    print(f"\n10. Получение полной информации о пользователе...")
    user_info = get_user_info(test_user_id)
    if user_info:
        print(f"    User ID: {user_info['user_id']}")
        print(f"    Username: {user_info['username']}")
        print(f"    First Name: {user_info['first_name']}")
        print(f"    Paid: {user_info['paid']}")
        print(f"    Paid Date: {user_info['paid_date']}")
        print(f"    Materials Sent: {user_info['materials_sent']}")
        print(f"    Created At: {user_info['created_at']}")
        print("✅ Информация получена успешно")
    else:
        print("❌ ОШИБКА: не удалось получить информацию")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    print("\nБот готов к работе!")
    print("Следующие шаги:")
    print("1. Получите токен бота от @BotFather")
    print("2. Получите ваш Telegram ID от @userinfobot")
    print("3. Обновите BOT_TOKEN и ADMIN_ID в main.py")
    print("4. Запустите бота: python main.py")
    print("\nПодробная инструкция: см. SETUP.md")

if __name__ == "__main__":
    try:
        test_user_flow()
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
