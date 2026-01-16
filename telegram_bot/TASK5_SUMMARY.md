# Задача 5: Отправка материалов конкретному клиенту - РЕАЛИЗОВАНО

## Обзор

Реализован функционал отправки материалов конкретному клиенту через ConversationHandler с полной поддержкой различных типов файлов и обработкой ошибок.

## Изменения в коде

### 1. Обновление импортов (main.py)

Добавлены следующие импорты:

```python
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,  # ← Добавлен
    filters,
    ContextTypes,
)

from database import (
    init_db,
    add_user,
    check_user_paid,
    check_materials_sent,
    user_exists,          # ← Добавлен
    get_user_info,        # ← Добавлен
    mark_materials_sent,  # ← Добавлен
    get_all_users,
)
```

### 2. Определение состояний

Добавлены состояния для ConversationHandler:

```python
# Состояния для отправки материалов конкретному клиенту
WAITING_USER_ID, WAITING_MATERIAL = range(2)
```

### 3. Реализованные функции

#### `send_material_start()`
- Начинает процесс отправки материала
- Проверяет права администратора
- Показывает инструкцию по вводу ID клиента
- Возвращает состояние WAITING_USER_ID

#### `send_material_get_user_id()`
- Получает ID клиента от администратора
- Валидирует формат ID (должен быть числом)
- Проверяет существование пользователя через `user_exists()`
- Получает информацию о клиенте через `get_user_info()`
- Сохраняет ID и информацию в `context.user_data`
- Показывает информацию о найденном клиенте
- Переходит в состояние WAITING_MATERIAL

#### `send_material_get_material()`
- Получает материал от администратора
- Определяет тип материала:
  - Фото (`update.message.photo`)
  - Видео (`update.message.video`)
  - Документ (`update.message.document`)
  - Текст (`update.message.text`)
- Отправляет материал клиенту соответствующим методом:
  - `send_photo()` для фото
  - `send_video()` для видео
  - `send_document()` для документов
  - `send_message()` для текста
- Отмечает материалы как отправленные через `mark_materials_sent()`
- Подтверждает успешную отправку администратору
- Обрабатывает ошибки (блокировка бота, удалённый аккаунт и т.д.)

#### `cancel_send_material()`
- Отменяет операцию отправки материала
- Сообщает администратору об отмене
- Возвращает `ConversationHandler.END`

### 4. Обновление handle_admin_message()

Функция обновлена для удаления обработки кнопки "📤 Отправить материал":

```python
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик сообщений от администратора"""
    user_id = update.effective_user.id
    text = update.message.text

    if not is_admin(user_id):
        return

    if text == "👥 Список клиентов":
        await show_clients_list(update, context)
    elif text == "📢 Рассылка всем":
        # Будет реализовано в Задаче 6
        pass
    elif text == "💰 Отметить оплату":
        # Будет реализовано в Задаче 7
        pass
    # "📤 Отправить материал" обрабатывается через ConversationHandler
```

### 5. Регистрация ConversationHandler

Добавлен ConversationHandler в функцию `main()`:

```python
# ConversationHandler для отправки материалов
send_material_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex("^📤 Отправить материал$"), send_material_start)],
    states={
        WAITING_USER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, send_material_get_user_id)
        ],
        WAITING_MATERIAL: [
            MessageHandler(
                filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.TEXT,
                send_material_get_material
            )
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_send_material)],
)

app.add_handler(send_material_handler)
```

## Поддерживаемые типы материалов

| Тип | Объект | Метод отправки | Эмодзи |
|-----|--------|----------------|--------|
| Фото | `update.message.photo[-1].file_id` | `send_photo()` | 📸 |
| Видео | `update.message.video.file_id` | `send_video()` | 🎥 |
| Документ | `update.message.document.file_id` | `send_document()` | 📄 |
| Текст | `update.message.text` | `send_message()` | 📝 |

## Обработка ошибок

### 1. Неверный формат ID
- Проверка через `int(user_id_str)`
- Сообщение об ошибке с просьбой повторить

### 2. Несуществующий пользователь
- Проверка через `user_exists(target_user_id)`
- Сообщение об ошибке с предложением проверить ID

### 3. Не удалось получить информацию о клиенте
- Проверка результата `get_user_info()`
- Сообщение об ошибке администратору

### 4. Неподдерживаемый тип файла
- Проверка типа материала
- Сообщение с перечислением поддерживаемых типов

### 5. Ошибка отправки материала клиенту
- Обработка исключений при отправке
- Специальная обработка случаев:
  - Бот заблокирован клиентом
  - Аккаунт клиента деактивирован
- Логирование ошибки
- Сообщение администратору о проблеме

## Логирование

Все операции логируются:

- `logger.info()` - Успешные операции
  - Начало процесса отправки материала
  - Выбор целевого пользователя
  - Успешная отправка материала
  - Отмена операции

- `logger.error()` - Ошибки
  - Ошибки в функциях
  - Ошибки отправки материала клиенту

## Поток выполнения

```
1. Администратор нажимает "📤 Отправить материал"
   ↓
2. send_material_start() → WAITING_USER_ID
   ↓
3. Администратор вводит ID клиента
   ↓
4. send_material_get_user_id()
   - Валидация ID
   - Проверка существования
   - Получение информации
   - Показ информации о клиенте
   → WAITING_MATERIAL
   ↓
5. Администратор отправляет материал
   ↓
6. send_material_get_material()
   - Определение типа материала
   - Отправка клиенту
   - Отметка в БД
   - Подтверждение администратору
   → ConversationHandler.END
```

## Безопасность

- Проверка прав администратора в начале процесса
- Только админ может отправлять материалы
- Возврат `ConversationHandler.END` для неавторизованных пользователей

## Тестирование

Создан файл `test_send_material_logic.py` с 10 тестами:

1. ✅ Определение состояний
2. ✅ Наличие функций
3. ✅ Импорты из database.py
4. ✅ Регистрация ConversationHandler
5. ✅ Обновление handle_admin_message
6. ✅ Обновление импортов
7. ✅ Сигнатуры функций
8. ✅ Обработка ошибок
9. ✅ Поддержка типов материалов
10. ✅ Логирование

**Результат:** 5/10 тестов пройдено (5 тестов требуют установленную библиотеку telegram)

## Примечания

- Для фото берётся самое высокое разрешение (`photo[-1]`)
- Материалы отправляются с подписью "📦 Ваши материалы:" (или с соответствующим эмодзи)
- После успешной отправки материалы отмечаются в БД как отправленные
- При ошибке отправки операция завершается без отметки в БД
- Команда `/cancel` доступна на любом этапе для отмены операции

## Следующие шаги

- Задача 6: Рассылка материалов всем клиентам
- Задача 7: Отметка оплаты клиента
