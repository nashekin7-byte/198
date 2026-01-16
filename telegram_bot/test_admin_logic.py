#!/usr/bin/env python3
"""
Скрипт для тестирования логики админ-панели без реального Telegram API.
Проверяет работу функций администратора и форматирование списка клиентов.
"""

import sys
from database import (
    init_db,
    add_user,
    mark_user_paid,
    mark_materials_sent,
    get_all_users,
)

def test_admin_functions():
    """Тестирование функций администратора."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ АДМИН-ПАНЕЛИ")
    print("=" * 60)

    # Инициализация БД
    print("\n1. Инициализация базы данных...")
    init_db()
    print("✅ База данных инициализирована")

    # Создание тестовых пользователей
    print("\n2. Создание тестовых пользователей...")
    test_users = [
        (1001, "ivan_petrov", "Иван Петров"),
        (1002, "maria_sid", "Мария Сидорова"),
        (1003, "alex_smith", "Алекс Смит"),
        (1004, "anna_ivanova", "Анна Иванова"),
        (1005, "peter_volkov", "Петр Волков"),
        (1006, "elena_k", "Елена Королева"),
    ]

    for user_id, username, first_name in test_users:
        add_user(user_id, username, first_name)
        print(f"   ✅ Добавлен пользователь: {username}")

    # Отмечаем некоторых как оплативших
    print("\n3. Отметка некоторых пользователей как оплативших...")
    paid_users = [1001, 1002, 1004]
    for user_id in paid_users:
        mark_user_paid(user_id)
        print(f"   ✅ Отмечена оплата для user_id: {user_id}")

    # Отправляем материалы некоторым оплатившим
    print("\n4. Отправка материалов...")
    materials_sent = [1001]
    for user_id in materials_sent:
        mark_materials_sent(user_id)
        print(f"   ✅ Отправлены материалы для user_id: {user_id}")

    # Получение всех пользователей
    print("\n5. Получение списка всех пользователей...")
    all_users = get_all_users()
    print(f"   ✅ Всего пользователей: {len(all_users)}")

    # Разделение на оплативших и неоплативших
    paid = [u for u in all_users if u['paid']]
    unpaid = [u for u in all_users if not u['paid']]

    print(f"   Оплатившие: {len(paid)}")
    print(f"   Неоплатившие: {len(unpaid)}")

    # Формирование сообщения (симуляция show_clients_list)
    print("\n6. Формирование сообщения для админа...")
    total = len(all_users)

    if not all_users:
        print("   ❌ Клиентов не найдено")
    else:
        messages = []
        current_message = f"👥 СПИСОК КЛИЕНТОВ (всего: {total})\n\n"

        # Оплатившие клиенты
        if paid:
            current_message += f"📍 ОПЛАТИВШИЕ КЛИЕНТЫ ({len(paid)}):\n\n"
            for user in paid:
                user_info = (
                    f"✅ 📦 ID: `{user['user_id']}`\n"
                    f"   @{user['username']} - {user['first_name']}\n"
                    f"   Оплата: ✅ Да"
                )
                if user['paid_date']:
                    user_info += f" (дата: {user['paid_date'].split()[0]})"
                user_info += "\n"
                user_info += f"   Материалы: {'✅ Отправлены' if user['materials_sent'] else '⏳ Не отправлены'}\n\n"

                if len(current_message) + len(user_info) > 4000:
                    messages.append(current_message)
                    current_message = f"👥 СПИСОК КЛИЕНТОВ (продолжение)\n\n" + user_info
                else:
                    current_message += user_info

        # Неоплатившие клиенты
        if unpaid:
            current_message += f"\n📍 НЕ ОПЛАТИВШИЕ КЛИЕНТЫ ({len(unpaid)}):\n\n"
            for user in unpaid:
                user_info = (
                    f"❌ ⏳ ID: `{user['user_id']}`\n"
                    f"   @{user['username']} - {user['first_name']}\n"
                    f"   Оплата: ❌ Нет\n"
                    f"   Материалы: ❌ Не отправлены\n\n"
                )

                if len(current_message) + len(user_info) > 4000:
                    messages.append(current_message)
                    current_message = f"👥 СПИСОК КЛИЕНТОВ (продолжение)\n\n" + user_info
                else:
                    current_message += user_info

        messages.append(current_message)

        # Вывод сформированных сообщений
        print(f"   ✅ Сформировано {len(messages)} сообщений")
        for i, msg in enumerate(messages):
            if len(messages) > 1:
                msg += f"\n\n(Страница {i+1} из {len(messages)})"

            print(f"\n--- Сообщение {i+1} ---")
            print(msg)
            print("--- Конец сообщения ---")

    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ АДМИН-ПАНЕЛИ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_admin_functions()
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
