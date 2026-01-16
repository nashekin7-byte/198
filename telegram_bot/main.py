import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from database import (
    init_db,
    add_user,
    check_user_paid,
    check_materials_sent,
    get_all_users,
)

# Определение путей относительно расположения файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Создание директории для логов, если её нет
os.makedirs(LOG_DIR, exist_ok=True)

# Конфигурация логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'bot.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Константы (позже переместить в config.py)
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Получить от @BotFather в Telegram
ADMIN_ID = 123456789  # Получить через @userinfobot

# Клавиатуры
def get_main_keyboard():
    """Основное меню для клиентов"""
    keyboard = [
        ["💳 Оплатить", "📊 Мой статус"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Добавить пользователя в БД
        add_user(user.id, user.username or "No username", user.first_name or "User")
        
        # Показать приветствие
        welcome_text = (
            f"👋 Добро пожаловать в наш сервис, {user.first_name}!\n\n"
            "Здесь вы можете:\n"
            "✅ Оплатить доступ и получить эксклюзивные материалы\n"
            "✅ Проверить статус вашей оплаты\n\n"
            "Выберите действие из меню ниже."
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка. Попробуйте позже."
        )

async def payment_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки 'Оплатить'"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        # Проверить, оплачивал ли уже
        if check_user_paid(user_id):
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "✅ Вы уже произвели оплату!\n\n"
                    "Материалы будут отправлены вам вскоре.\n"
                    "Проверьте статус командой /status"
                )
            )
        else:
            # Показать реквизиты
            payment_text = (
                "💳 РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ\n\n"
                "Сумма: 1500 ₽\n\n"
                "Номер карты:\n"
                "2200 1234 5678 9012\n\n"
                "После оплаты администратор проверит платеж и отправит вам материалы.\n\n"
                f"⚠️ Ваш ID для связи с администратором:\n"
                f"`{user_id}`\n"
                f"(можно скопировать)\n\n"
                "Если у вас возникли вопросы - напишите администратору."
            )
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=payment_text,
                parse_mode='Markdown'
            )
        
        logger.info(f"User {user_id} requested payment details")
        
    except Exception as e:
        logger.error(f"Error in payment_button handler: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при обработке платежа."
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status и кнопки 'Мой статус'"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        paid = check_user_paid(user_id)
        materials_sent = check_materials_sent(user_id)
        
        if not paid:
            status_text = (
                "❌ СТАТУС ОПЛАТЫ: Не получена\n\n"
                "Для получения доступа оплатите 1500 ₽\n"
                "Используйте кнопку \"💳 Оплатить\" для просмотра реквизитов."
            )
        elif paid and not materials_sent:
            status_text = (
                "✅ СТАТУС ОПЛАТЫ: Получена\n\n"
                "⏳ СТАТУС МАТЕРИАЛОВ: В процессе обработки\n\n"
                "Администратор проверит платеж и отправит вам материалы в ближайшее время."
            )
        else:  # paid and materials_sent
            status_text = (
                "✅ СТАТУС ОПЛАТЫ: Получена\n"
                "✅ СТАТУС МАТЕРИАЛОВ: Отправлены\n\n"
                "Спасибо за покупку! Материалы успешно отправлены вам.\n"
                "Если у вас возникли проблемы с доступом - напишите администратору."
            )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=status_text,
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"User {user_id} checked status: paid={paid}, materials={materials_sent}")
        
    except Exception as e:
        logger.error(f"Error in status_command handler: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при проверке статуса."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Универсальный обработчик сообщений для кнопок"""
    text = update.message.text

    if text == "💳 Оплатить":
        await payment_button(update, context)
    elif text == "📊 Мой статус":
        await status_command(update, context)
    else:
        # На неизвестные сообщения не реагировать
        pass

# Admin functions
def is_admin(user_id):
    """Проверка прав администратора"""
    return user_id == ADMIN_ID

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /admin"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_admin(user_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="⛔ У вас нет доступа к админ-панели"
        )
        logger.warning(f"Unauthorized admin access attempt from user {user_id}")
        return

    try:
        admin_text = "⚙️ АДМИН-ПАНЕЛЬ\n\nУправление клиентами и материалами"

        admin_keyboard = [
            ["👥 Список клиентов"],
            ["📤 Отправить материал", "📢 Рассылка всем"],
            ["💰 Отметить оплату"],
        ]

        await context.bot.send_message(
            chat_id=chat_id,
            text=admin_text,
            reply_markup=ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
        )

        logger.info(f"Admin {user_id} opened admin panel")

    except Exception as e:
        logger.error(f"Error in admin_command: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при открытии админ-панели."
        )

async def show_clients_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список всех клиентов"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_admin(user_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="⛔ У вас нет доступа к админ-панели"
        )
        return

    try:
        all_users = get_all_users()

        if not all_users:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Клиентов не найдено"
            )
            return

        # Разделить на оплатившие и неоплатившие
        paid_users = [u for u in all_users if u['paid']]
        unpaid_users = [u for u in all_users if not u['paid']]

        total = len(all_users)

        # Формировать сообщение с разбиением на страницы
        messages = []
        current_message = f"👥 СПИСОК КЛИЕНТОВ (всего: {total})\n\n"

        # Оплатившие клиенты
        if paid_users:
            current_message += f"📍 ОПЛАТИВШИЕ КЛИЕНТЫ ({len(paid_users)}):\n\n"
            for user in paid_users:
                user_info = (
                    f"✅ 📦 ID: `{user['user_id']}`\n"
                    f"   @{user['username']} - {user['first_name']}\n"
                    f"   Оплата: ✅ Да"
                )
                if user['paid_date']:
                    user_info += f" (дата: {user['paid_date'].split()[0]})"
                user_info += "\n"
                user_info += f"   Материалы: {'✅ Отправлены' if user['materials_sent'] else '⏳ Не отправлены'}\n\n"

                if len(current_message) + len(user_info) > 4000:  # Лимит Telegram
                    messages.append(current_message)
                    current_message = f"👥 СПИСОК КЛИЕНТОВ (продолжение)\n\n" + user_info
                else:
                    current_message += user_info

        # Неоплатившие клиенты
        if unpaid_users:
            current_message += f"\n📍 НЕ ОПЛАТИВШИЕ КЛИЕНТЫ ({len(unpaid_users)}):\n\n"
            for user in unpaid_users:
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

        # Отправить все сообщения
        for i, msg in enumerate(messages):
            if len(messages) > 1:
                msg += f"\n\n(Страница {i+1} из {len(messages)})"

            await context.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode='Markdown'
            )

        logger.info(f"Admin {user_id} viewed clients list. Total: {total}, Paid: {len(paid_users)}, Unpaid: {len(unpaid_users)}")

    except Exception as e:
        logger.error(f"Error in show_clients_list: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при загрузке списка клиентов."
        )

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик сообщений от администратора"""
    user_id = update.effective_user.id
    text = update.message.text

    if not is_admin(user_id):
        return

    if text == "👥 Список клиентов":
        await show_clients_list(update, context)
    elif text == "📤 Отправить материал":
        # Будет реализовано в Задаче 5
        pass
    elif text == "📢 Рассылка всем":
        # Будет реализовано в Задаче 6
        pass
    elif text == "💰 Отметить оплату":
        # Будет реализовано в Задаче 7
        pass

def main():
    """Запуск бота"""
    # Инициализировать БД
    init_db()
    logger.info("Database initialized")
    
    # Создать Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавить обработчики в правильном порядке
    # Сначала команды, потом остальное
    # Обработчики для клиентов
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))

    # Обработчики для администратора
    app.add_handler(CommandHandler("admin", admin_command))

    # Универсальный обработчик сообщений для кнопок
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
    
    # Запустить бота
    logger.info("Bot started polling")
    app.run_polling()

if __name__ == "__main__":
    main()
