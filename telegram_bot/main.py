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

def main():
    """Запуск бота"""
    # Инициализировать БД
    init_db()
    logger.info("Database initialized")
    
    # Создать Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавить обработчики в правильном порядке
    # Сначала команды, потом остальное
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запустить бота
    logger.info("Bot started polling")
    app.run_polling()

if __name__ == "__main__":
    main()
