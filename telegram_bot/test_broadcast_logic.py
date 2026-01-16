#!/usr/bin/env python3
"""
Скрипт для тестирования логики рассылки материалов без реального Telegram API.
Проверяет работу функций рассылки и взаимодействие с базой данных.
"""

import sys
import os
import sqlite3
from database import (
    init_db,
    add_user,
    mark_user_paid,
    get_paid_users,
    get_paid_users_count,
)

def clear_database():
    """Очистка базы данных для тестов."""
    from database import BASE_DIR
    db_path = os.path.join(BASE_DIR, 'bot_data', 'bot.db')
    if os.path.exists(db_path):
        os.remove(db_path)

def test_broadcast_functions():
    """Тестирование функций рассылки материалов."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЛОГИКИ РАССЫЛКИ")
    print("=" * 60)

    # Очистка и инициализация БД
    print("\n1. Очистка и инициализация базы данных...")
    clear_database()
    init_db()
    print("✅ База данных инициализирована")

    # Создание тестовых пользователей
    print("\n2. Создание тестовых пользователей...")
    test_users = [
        (2001, "user1", "Пользователь 1"),
        (2002, "user2", "Пользователь 2"),
        (2003, "user3", "Пользователь 3"),
        (2004, "user4", "Пользователь 4"),
        (2005, "user5", "Пользователь 5"),
    ]

    for user_id, username, first_name in test_users:
        add_user(user_id, username, first_name)
        print(f"   ✅ Добавлен пользователь: {username}")

    # Отмечаем некоторых как оплативших
    print("\n3. Отметка некоторых пользователей как оплативших...")
    paid_users = [2001, 2002, 2003]
    for user_id in paid_users:
        mark_user_paid(user_id)
        print(f"   ✅ Отмечена оплата для user_id: {user_id}")

    # Тестирование get_paid_users_count
    print("\n4. Тестирование get_paid_users_count()...")
    count = get_paid_users_count()
    print(f"   Количество оплативших: {count}")
    if count == len(paid_users):
        print("   ✅ Количество оплативших корректно")
    else:
        print(f"   ❌ ОШИБКА: ожидалось {len(paid_users)}, получено {count}")
        sys.exit(1)

    # Тестирование get_paid_users
    print("\n5. Тестирование get_paid_users()...")
    paid_user_ids = get_paid_users()
    print(f"   ID оплативших пользователей: {paid_user_ids}")
    
    # Проверка что все оплатившие пользователи присутствуют
    expected_ids = set(paid_users)
    actual_ids = set(paid_user_ids)
    
    if expected_ids == actual_ids:
        print("   ✅ Список оплативших пользователей корректен")
    else:
        print(f"   ❌ ОШИБКА: ожидалось {expected_ids}, получено {actual_ids}")
        sys.exit(1)

    # Тестирование сценария без оплативших пользователей
    print("\n6. Тестирование сценария без оплативших пользователей...")
    
    # Очистка и создание новой БД для теста
    clear_database()
    init_db()
    
    # Добавляем пользователя без оплаты
    add_user(3001, "no_pay_user", "Без Оплат")
    
    count = get_paid_users_count()
    if count == 0:
        print("   ✅ Корректно: 0 оплативших пользователей")
    else:
        print(f"   ❌ ОШИБКА: ожидалось 0, получено {count}")
        sys.exit(1)
    
    paid_user_ids = get_paid_users()
    if len(paid_user_ids) == 0:
        print("   ✅ Корректно: пустой список оплативших")
    else:
        print(f"   ❌ ОШИБКА: ожидался пустой список, получено {paid_user_ids}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ РАССЫЛКИ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    print("\nФункции рассылки готовы к работе!")
    print("Они будут использоваться в broadcast_send_material для отправки")
    print("материалов всем оплатившим клиентам.")

if __name__ == "__main__":
    try:
        test_broadcast_functions()
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)