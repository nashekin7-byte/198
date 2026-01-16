"""
Тесты для функционала отправки материалов конкретному клиенту (Задача 5)

Тестируются:
1. Инициализация ConversationHandler
2. Функция send_material_start
3. Функция send_material_get_user_id
4. Функция send_material_get_material
5. Функция cancel_send_material
6. Обработка различных типов материалов
7. Обработка ошибок
"""

import logging
import sys
import os

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_states_defined():
    """Проверка, что состояния определены"""
    logger.info("=== Тест 1: Проверка определения состояний ===")

    try:
        from main import WAITING_USER_ID, WAITING_MATERIAL

        assert WAITING_USER_ID == 0, "WAITING_USER_ID должно быть равно 0"
        assert WAITING_MATERIAL == 1, "WAITING_MATERIAL должно быть равно 1"

        logger.info("✅ Состояния определены корректно")
        logger.info(f"   WAITING_USER_ID = {WAITING_USER_ID}")
        logger.info(f"   WAITING_MATERIAL = {WAITING_MATERIAL}")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_functions_exist():
    """Проверка, что все функции определены"""
    logger.info("\n=== Тест 2: Проверка наличия функций ===")

    try:
        from main import (
            send_material_start,
            send_material_get_user_id,
            send_material_get_material,
            cancel_send_material
        )

        functions = [
            send_material_start,
            send_material_get_user_id,
            send_material_get_material,
            cancel_send_material
        ]

        function_names = [
            "send_material_start",
            "send_material_get_user_id",
            "send_material_get_material",
            "cancel_send_material"
        ]

        for func, name in zip(functions, function_names):
            assert callable(func), f"{name} должна быть вызываемой функцией"
            logger.info(f"✅ Функция {name} существует")

        logger.info("✅ Все функции определены корректно")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_database_imports():
    """Проверка импортов из database.py"""
    logger.info("\n=== Тест 3: Проверка импортов из database.py ===")

    try:
        from main import (
            user_exists,
            get_user_info,
            mark_materials_sent
        )

        assert callable(user_exists), "user_exists должна быть функцией"
        assert callable(get_user_info), "get_user_info должна быть функцией"
        assert callable(mark_materials_sent), "mark_materials_sent должна быть функцией"

        logger.info("✅ Все функции database.py импортированы корректно")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_conversation_handler_registration():
    """Проверка регистрации ConversationHandler"""
    logger.info("\n=== Тест 4: Проверка регистрации ConversationHandler ===")

    try:
        # Проверяем, что в main.py есть код регистрации ConversationHandler
        with open('/home/engine/project/telegram_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            'send_material_handler = ConversationHandler(',
            'WAITING_USER_ID',
            'WAITING_MATERIAL',
            'send_material_start',
            'send_material_get_user_id',
            'send_material_get_material',
            'cancel_send_material',
            'app.add_handler(send_material_handler)'
        ]

        for check in checks:
            assert check in content, f"В коде должна быть строка: {check}"
            logger.info(f"✅ Найдено: {check}")

        logger.info("✅ ConversationHandler зарегистрирован корректно")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Файл не найден: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_handle_admin_message_updated():
    """Проверка обновления handle_admin_message"""
    logger.info("\n=== Тест 5: Проверка обновления handle_admin_message ===")

    try:
        with open('/home/engine/project/telegram_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем, что "📤 Отправить материал" больше не обрабатывается в handle_admin_message
        assert '"📤 Отправить материал" обрабатывается через ConversationHandler' in content, \
            "Должен быть комментарий о ConversationHandler"

        # Проверяем, что нет pass для "📤 Отправить материал"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '"📤 Отправить материал"' in line and i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                assert next_line != 'pass', 'Не должно быть pass для "📤 Отправить материал"'

        logger.info("✅ Функция handle_admin_message обновлена корректно")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Файл не найден: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_imports_updated():
    """Проверка обновления импортов"""
    logger.info("\n=== Тест 6: Проверка обновления импортов ===")

    try:
        from telegram.ext import ConversationHandler
        from telegram.ext import CommandHandler
        from main import user_exists, get_user_info, mark_materials_sent

        logger.info("✅ ConversationHandler импортирован")
        logger.info("✅ CommandHandler импортирован")
        logger.info("✅ user_exists импортирован")
        logger.info("✅ get_user_info импортирован")
        logger.info("✅ mark_materials_sent импортирован")

        logger.info("✅ Все импорты обновлены корректно")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False


def test_function_signatures():
    """Проверка сигнатур функций"""
    logger.info("\n=== Тест 7: Проверка сигнатур функций ===")

    try:
        from main import (
            send_material_start,
            send_material_get_user_id,
            send_material_get_material,
            cancel_send_material
        )
        import inspect

        # Проверяем send_material_start
        sig = inspect.signature(send_material_start)
        params = list(sig.parameters.keys())
        assert 'update' in params, "send_material_start должна принимать update"
        assert 'context' in params, "send_material_start должна принимать context"
        logger.info("✅ send_material_start имеет правильную сигнатуру")

        # Проверяем send_material_get_user_id
        sig = inspect.signature(send_material_get_user_id)
        params = list(sig.parameters.keys())
        assert 'update' in params, "send_material_get_user_id должна принимать update"
        assert 'context' in params, "send_material_get_user_id должна принимать context"
        logger.info("✅ send_material_get_user_id имеет правильную сигнатуру")

        # Проверяем send_material_get_material
        sig = inspect.signature(send_material_get_material)
        params = list(sig.parameters.keys())
        assert 'update' in params, "send_material_get_material должна принимать update"
        assert 'context' in params, "send_material_get_material должна принимать context"
        logger.info("✅ send_material_get_material имеет правильную сигнатуру")

        # Проверяем cancel_send_material
        sig = inspect.signature(cancel_send_material)
        params = list(sig.parameters.keys())
        assert 'update' in params, "cancel_send_material должна принимать update"
        assert 'context' in params, "cancel_send_material должна принимать context"
        logger.info("✅ cancel_send_material имеет правильную сигнатуру")

        logger.info("✅ Все функции имеют правильные сигнатуры")
        return True

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_error_handling():
    """Проверка обработки ошибок"""
    logger.info("\n=== Тест 8: Проверка обработки ошибок ===")

    try:
        with open('/home/engine/project/telegram_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем наличие try-except блоков
        checks = [
            'try:',
            'except Exception as e:',
            'logger.error',
            'ConversationHandler.END'
        ]

        # Проверяем в send_material_get_user_id
        send_material_get_user_id_section = content[content.find('async def send_material_get_user_id'):
                                                       content.find('async def send_material_get_material')]

        for check in ['try:', 'except ValueError:', 'except Exception as e:']:
            assert check in send_material_get_user_id_section, \
                f"В send_material_get_user_id должен быть {check}"
            logger.info(f"✅ send_material_get_user_id содержит {check}")

        # Проверяем в send_material_get_material
        send_material_get_material_section = content[content.find('async def send_material_get_material'):
                                                     content.find('async def cancel_send_material')]

        assert 'blocked' in send_material_get_material_section or 'user is deactivated' in send_material_get_material_section, \
            "send_material_get_material должна обрабатывать случай блокировки бота"
        logger.info("✅ send_material_get_material обрабатывает случай блокировки бота")

        logger.info("✅ Обработка ошибок реализована корректно")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Файл не найден: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_material_types_support():
    """Проверка поддержки различных типов материалов"""
    logger.info("\n=== Тест 9: Проверка поддержки типов материалов ===")

    try:
        with open('/home/engine/project/telegram_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем поддержку всех типов материалов
        material_types = [
            'update.message.photo',
            'update.message.video',
            'update.message.document',
            'update.message.text'
        ]

        # Проверяем в send_material_get_material
        send_material_get_material_section = content[content.find('async def send_material_get_material'):
                                                     content.find('async def cancel_send_material')]

        for material_type in material_types:
            assert material_type in send_material_get_material_section, \
                f"Должна быть поддержка {material_type}"
            logger.info(f"✅ Поддерживается {material_type}")

        # Проверяем методы отправки
        send_methods = [
            'send_photo',
            'send_video',
            'send_document',
            'send_message'
        ]

        for send_method in send_methods:
            assert send_method in send_material_get_material_section, \
                f"Должен использоваться метод {send_method}"
            logger.info(f"✅ Используется метод {send_method}")

        logger.info("✅ Все типы материалов поддерживаются")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Оайл не найден: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def test_logging():
    """Проверка логирования"""
    logger.info("\n=== Тест 10: Проверка логирования ===")

    try:
        with open('/home/engine/project/telegram_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем наличие логирования в функциях
        functions = [
            'send_material_start',
            'send_material_get_user_id',
            'send_material_get_material',
            'cancel_send_material'
        ]

        for func_name in functions:
            # Находим секцию функции
            start = content.find(f'async def {func_name}')
            end = content.find('async def ', start + 1) if start != -1 else -1
            if end == -1:
                end = len(content)

            func_section = content[start:end]

            assert 'logger.' in func_section, f"{func_name} должна содержать логирование"
            logger.info(f"✅ {func_name} содержит логирование")

        logger.info("✅ Логирование реализовано корректно")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Файл не найден: {e}")
        return False
    except AssertionError as e:
        logger.error(f"❌ Ошибка утверждения: {e}")
        return False


def main():
    """Запуск всех тестов"""
    logger.info("=" * 60)
    logger.info("НАЧАЛО ТЕСТИРОВАНИЯ ЗАДАЧИ 5: ОТПРАВКА МАТЕРИАЛОВ")
    logger.info("=" * 60)

    tests = [
        ("Определение состояний", test_states_defined),
        ("Наличие функций", test_functions_exist),
        ("Импорты из database.py", test_database_imports),
        ("Регистрация ConversationHandler", test_conversation_handler_registration),
        ("Обновление handle_admin_message", test_handle_admin_message_updated),
        ("Обновление импортов", test_imports_updated),
        ("Сигнатуры функций", test_function_signatures),
        ("Обработка ошибок", test_error_handling),
        ("Поддержка типов материалов", test_material_types_support),
        ("Логирование", test_logging),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Тест '{test_name}' завершился с исключением: {e}")
            results.append((test_name, False))

    # Итоговая статистика
    logger.info("\n" + "=" * 60)
    logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        logger.info(f"{status}: {test_name}")

    logger.info("\n" + "=" * 60)
    logger.info(f"ИТОГО: {passed}/{total} тестов пройдено")
    logger.info("=" * 60)

    if passed == total:
        logger.info("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} тест(ов) не пройдено")
        return 1


if __name__ == "__main__":
    sys.exit(main())
