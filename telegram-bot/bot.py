#!/usr/bin/env python3
"""
White Clinic Telegram Bot
Dental clinic assistant bot with full functionality
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Clinic information
CLINIC_INFO = {
    "name": "White clinic",
    "head_doctor": "Сунгуров Артем Валерьевич",
    "address": "ул. Коммунистов, 16, Череповец",
    "phone": "8 (820) 274-01-74",
    "website": "https://whiteclinic.ru",
    "telegram_channel": "@white_clinic_che",
    "working_hours": "09:00–21:00 (ежедневно, без выходных)",
    "working_hours_short": "09:00–21:00, ежедневно без выходных"
}

DOCTORS = [
    {
        "name": "Сунгуров Артем Валерьевич",
        "specialty": "стоматолог-хирург, руководитель",
        "experience": "10+ лет опыта",
        "description": "Высшее медицинское образование, специализация: хирургическая стоматология, постоянное повышение квалификации"
    },
    {
        "name": "Иванова Елена Сергеевна",
        "specialty": "стоматолог-терапевт",
        "experience": "8 лет опыта",
        "description": "Высшее медицинское образование, специализация: терапевтическая стоматология и эндодонтия"
    },
    {
        "name": "Петров Дмитрий Игоревич",
        "specialty": "стоматолог-ортопед",
        "experience": "6 лет опыта",
        "description": "Высшее медицинское образование, специализация: ортопедическая стоматология и протезирование"
    },
    {
        "name": "Коваленко Анна Алексеевна",
        "specialty": "гигиенист полости рта",
        "experience": "5 лет опыта",
        "description": "Высшее медицинское образование, специализация: профессиональная гигиена полости рта и профилактика заболеваний"
    }
]

# Services organized by category
SERVICES = {
    "ХИРУРГИЧЕСКАЯ СТОМАТОЛОГИЯ 💉": [
        "Удаление зубов любой сложности",
        "Удаление зубов мудрости",
        "Имплантация зубов",
        "Костная пластика",
        "Резекция верхушки корня"
    ],
    "ТЕРАПЕВТИЧЕСКАЯ СТОМАТОЛОГИЯ 🦷": [
        "Лечение кариеса",
        "Лечение пульпита и периодонтита",
        "Эстетическая реставрация зубов",
        "Профессиональная гигиена"
    ],
    "ОРТОПЕДИЯ 👑": [
        "Коронки (керамика, диоксид циркония)",
        "Виниры и вкладки",
        "Протезирование на имплантах",
        "Съёмное протезирование"
    ],
    "ЭСТЕТИЧЕСКАЯ СТОМАТОЛОГИЯ ✨": [
        "Отбеливание зубов",
        "Установка виниров",
        "Чистка и полировка"
    ]
}

# Pricing (displayed if PDF is not found)
PRICES = {
    "Удаление простое": "от 3 000 ₽",
    "Удаление сложное": "от 5 000 ₽",
    "Удаление зуба мудрости": "от 7 000 ₽",
    "Имплантация": "от 35 000 ₽",
    "Лечение кариеса": "от 5 000 ₽",
    "Коронка керамическая": "от 20 000 ₽",
    "Коронка циркониевая": "от 25 000 ₽"
}

# FAQ questions and answers
FAQ = [
    {
        "question": "Больно ли лечить зубы?",
        "answer": "Используем современную анестезию, которая делает процедуры максимально комфортными и безболезненными."
    },
    {
        "question": "Сколько стоит имплантация?",
        "answer": "Стоимость имплантации начинается от 35 000 ₽, окончательная цена определяется после диагностики и составления плана лечения."
    },
    {
        "question": "Как часто нужно посещать стоматолога?",
        "answer": "Рекомендуется профилактический осмотр раз в 6 месяцев для поддержания здоровья полости рта."
    },
    {
        "question": "Даёте ли вы гарантию?",
        "answer": "Да, мы предоставляем гарантию на все виды работ. Срок гарантии зависит от типа лечения и используемых материалов."
    },
    {
        "question": "Можно ли вылечить зуб за один визит?",
        "answer": "Во многих случаях да, особенно при лечении кариеса. Более сложные случаи могут требовать несколько посещений."
    },
    {
        "question": "Вы работаете без выходных?",
        "answer": "Да, мы работаем ежедневно с 09:00 до 21:00, без выходных."
    },
    {
        "question": "Есть ли рассрочка?",
        "answer": "Да, у нас доступна рассрочка на лечение. Детали можно уточнить при записи на приём."
    }
]

# Callback data constants
MAIN_MENU = "main_menu"
SHOW_SERVICES = "show_services"
SHOW_PRICES = "show_prices"
SEND_GUIDE = "send_guide"
SHOW_ABOUT = "show_about"
SHOW_APPOINTMENT = "show_appointment"
SHOW_FAQ = "show_faq"
SHUTDOWN = "shutdown"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show main menu"""
    user = update.effective_user
    
    welcome_text = (
        f"👋 Здравствуйте\\, {user.first_name}!\n\n"
        f"Меня зовут *{CLINIC_INFO['head_doctor']}*\\. Как руководитель *{CLINIC_INFO['name']}* я рад приветствовать вас в нашем боте!\n\n"
        f"*{CLINIC_INFO['name']}* — современная стоматологическая клиника в Череповце\\."
        f"Мы предлагаем полный спектр стоматологических услуг с использованием передовых технологий и качественных материалов\\."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Наши услуги", callback_data=SHOW_SERVICES)],
        [InlineKeyboardButton("💰 Прайс-лист", callback_data=SHOW_PRICES)],
        [InlineKeyboardButton("📚 Полезный гайд", callback_data=SEND_GUIDE)],
        [InlineKeyboardButton("👨‍⚕️ О нас", callback_data=SHOW_ABOUT)],
        [InlineKeyboardButton("📞 Записаться на приём", callback_data=SHOW_APPOINTMENT)],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data=SHOW_FAQ)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    welcome_text = (
        f"👋 Здравствуйте\\, {user.first_name}!\n\n"
        f"Меня зовут *{CLINIC_INFO['head_doctor']}*\\. Как руководитель *{CLINIC_INFO['name']}* я рад приветствовать вас!\n\n"
        f"*{CLINIC_INFO['name']}* — современная стоматологическая клиника в Череповце\\."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Наши услуги", callback_data=SHOW_SERVICES)],
        [InlineKeyboardButton("💰 Прайс-лист", callback_data=SHOW_PRICES)],
        [InlineKeyboardButton("📚 Полезный гайд", callback_data=SEND_GUIDE)],
        [InlineKeyboardButton("👨‍⚕️ О нас", callback_data=SHOW_ABOUT)],
        [InlineKeyboardButton("📞 Записаться на приём", callback_data=SHOW_APPOINTMENT)],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data=SHOW_FAQ)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        welcome_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show services menu"""
    query = update.callback_query
    await query.answer()
    
    services_text = "🦷 *НАШИ УСЛУГИ* \n\n"
    
    for category, items in SERVICES.items():
        services_text += f"*{category}*\n"
        for item in items:
            services_text += f"• {item}\n"
        services_text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Посмотреть цены", callback_data=SHOW_PRICES)],
        [InlineKeyboardButton("📞 Записаться на приём", callback_data=SHOW_APPOINTMENT)],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        services_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show price list"""
    query = update.callback_query
    await query.answer()
    
    pdf_path = Path("price_list.pdf")
    
    if pdf_path.exists():
        try:
            await query.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption=f"📄 Прайс-лист {CLINIC_INFO['name']}\nОкончательная стоимость определяется после осмотра"
            )
            return
        except Exception as e:
            logger.error(f"Error sending price list PDF: {e}")
    
    # Fallback to text prices if PDF doesn't exist or failed
    prices_text = "💰 *ПРАЙС-ЛИСТ*\n\n"
    for service, price in PRICES.items():
        prices_text += f"*{service}*: {price}\n"
    
    prices_text += f"\nℹ️ *Примечание*: Окончательная стоимость определяется после осмотра и составления плана лечения\\."
    
    keyboard = [
        [InlineKeyboardButton("📞 Записаться на приём", callback_data=SHOW_APPOINTMENT)],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        prices_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def send_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send dental care guide"""
    query = update.callback_query
    await query.answer()
    
    pdf_path = Path("dental_guide.pdf")
    
    if pdf_path.exists():
        try:
            await query.message.reply_document(
                document=open(pdf_path, 'rb'),
                caption=f"📚 Полезный гайд по уходу за зубами от {CLINIC_INFO['name']}"
            )
            return
        except Exception as e:
            logger.error(f"Error sending guide PDF: {e}")
    
    # Fallback to text guide if PDF doesn't exist or failed
    guide_text = "📚 *ПОЛЕЗНЫЙ ГАЙД*\n\nРекомендации по уходу за зубами:\n\n"
    guide_text += "💠 *Чистите зубы 2 раза в день* по 2\\-3 минуты\n\n"
    guide_text += "💠 *Используйте зубную нить* ежедневно\n\n"
    guide_text += "💠 *Избегайте перекусов* между приёмами пищи\n\n"
    guide_text += "💠 *Пейте больше воды*\n\n"
    guide_text += "💠 *Посещайте стоматолога раз в полгода* для профилактики"
    
    keyboard = [
        [InlineKeyboardButton("📅 Записаться на осмотр", callback_data=SHOW_APPOINTMENT)],
        [InlineKeyboardButton("📋 Посмотреть услуги", callback_data=SHOW_SERVICES)],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        guide_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show about information"""
    query = update.callback_query
    await query.answer()
    
    about_text = "👨‍⚕️ *О НАС*\n\n"
    
    # Head doctor info
    head_doctor = DOCTORS[0]
    about_text += f"*👨‍⚕️ СУНГУРОВ АРТЕМ ВАЛЕРЬЕВИЧ*\n"
    about_text += f"*{head_doctor['name']}*\n"
    about_text += f"_{head_doctor['specialty']}_\n"
    about_text += f"Опыт работы: {head_doctor['experience']}\n\n"
    about_text += f"{head_doctor['description']}\n\n\n"
    
    # Clinic info
    about_text += f"*🏥 О БЕЛОЙ КЛИНИКЕ:*\n\n"
    about_text += f"• Современное оборудование\n"
    about_text += f"• Опытная команда специалистов\n"
    about_text += f"• Индивидуальный подход к каждому пациенту\n"
    about_text += f"• Доступные цены\n"
    about_text += f"• Гарантия на все виды работ\n\n"
    about_text += f"*Наша команда врачей:*\n"
    for i, doctor in enumerate(DOCTORS, 1):
        about_text += f"{i}\\. {doctor['name']}\n   _{doctor['specialty']}_\n"
    about_text += "\n\n"
    
    about_text += f"*🏆 НАШИ ПРЕИМУЩЕСТВА:*\n\n"
    about_text += "• Безболезненное лечение\n"
    about_text += "• Современные методики\n"
    about_text += "• Качественные материалы\n"
    about_text += "• Прозрачное ценообразование\n"
    about_text += f"• Гибкий график работы ({CLINIC_INFO['working_hours_short']})\n\n"
    
    about_text += f"*📞 Контакты:*\n"
    about_text += f"Телефон: {CLINIC_INFO['phone']}\n"
    about_text += f"Telegram: {CLINIC_INFO['telegram_channel']}\n"
    about_text += f"Адрес: {CLINIC_INFO['address']}\n"
    about_text += f"Режим работы: {CLINIC_INFO['working_hours']}"
    
    keyboard = [
        [InlineKeyboardButton("✉️ Написать в Telegram", url=f"https://t.me/{CLINIC_INFO['telegram_channel'][1:]}")],
        [InlineKeyboardButton("🌐 Перейти на сайт", url=CLINIC_INFO['website'])],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        about_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def show_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show appointment information"""
    query = update.callback_query
    await query.answer()
    
    appointment_text = "📞 *ЗАПИСАТЬСЯ НА ПРИЁМ*\n"
    appointment_text += "📱 *Контакты:*\n\n"
    appointment_text += "Телефон: 8 \\(820\\) 274\\-01\\-74\n"
    appointment_text += "Telegram: @white_clinic_che\n"
    appointment_text += "Сайт: whiteclinic\\.ru\n\n"
    appointment_text += "⏰ *Режим работы:*\n"
    appointment_text += "09:00–21:00 \\(ежедневно, без выходных\\)\n\n"
    appointment_text += "📍 *Адрес:*\n"
    appointment_text += "Череповец, ул\\. Коммунистов, 16\n"
    appointment_text += "\\(Индустриальный район, ост\\. «Площадь Милютина»\\)\n\n"
    appointment_text += "💬 *Напишите нам в Telegram или позвоните, чтобы выбрать удобное время визита\\!"
    
    keyboard = [
        [InlineKeyboardButton("Написать в Telegram", url="https://t.me/white_clinic_che")],
        [InlineKeyboardButton("Позвонить", url="tel:+78202740174")],
        [InlineKeyboardButton("Открыть сайт", url="https://whiteclinic.ru")],
        [InlineKeyboardButton("Главное меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        appointment_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show frequently asked questions"""
    query = update.callback_query
    await query.answer()
    
    faq_text = "❓ *ЧАСТЫЕ ВОПРОСЫ*\n\n"
    
    for item in FAQ:
        faq_text += f"*❔ {item['question']}*\n"
        faq_text += f"✅ *{item['answer']}*\n\n"
    
    keyboard = [
        [InlineKeyboardButton("💬 Задать свой вопрос", url=f"https://t.me/{CLINIC_INFO['telegram_channel'][1:]}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        faq_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "*🤖 СПРАВКА ПО БОТУ*\n\n"
        "Этот бот поможет вам:\n"
        "• Узнать о наших услугах\n"
        "• Просмотреть актуальные цены\n"
        "• Получить полезные рекомендации по уходу\n"
        "• Записаться на приём\n"
        "• Задать интересующие вопросы\n\n"
        "*Команды бота:*\n"
        "/start — главное меню\n"
        "/help — эта справка\n"
        "/privacy — политика конфиденциальности\n\n"
        f"*Контакты {CLINIC_INFO['name']}:*\n"
        f"📞 {CLINIC_INFO['phone']}\n"
        f"📱 {CLINIC_INFO['telegram_channel']}\n"
        f"📍 {CLINIC_INFO['address']}\n"
        f"⏰ {CLINIC_INFO['working_hours']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /privacy command"""
    privacy_text = (
        "*🔒 ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ*\n\n"
        "Мы обеспечиваем полную конфиденциальность ваших данных:\n\n"
        "• Мы не передаём ваши данные третьим лицам\n"
        "• Вся информация используется только для связи с вами\n"
        "• Вы можете удалить свой аккаунт и данные в любой момент\n"
        "• Мы соблюдаем закон о защите персональных данных\n\n"
        "Для удаления данных напишите нам: @white_clinic_che\n"
        f"Версия: 1.0 | {CLINIC_INFO['name']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        privacy_text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages - redirect to buttons"""
    user = update.effective_user
    
    text = (
        f"{user.first_name}, используйте кнопки в меню для навигации\\!\n\n"
        f"Если у вас есть вопросы, свяжитесь с нами удобным для вас способом:\n\n"
        f"📱 Telegram: {CLINIC_INFO['telegram_channel']}\n"
        f"📞 Телефон: {CLINIC_INFO['phone']}\n"
        f"🌐 Сайт: {CLINIC_INFO['website']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("✉️ Написать в Telegram", url=f"https://t.me/{CLINIC_INFO['telegram_channel'][1:]}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all button clicks"""
    query = update.callback_query
    
    if query.data == MAIN_MENU or query.data == "menu":
        await main_menu(update, context)
    elif query.data == SHOW_SERVICES:
        await show_services(update, context)
    elif query.data == SHOW_PRICES:
        await show_prices(update, context)
    elif query.data == SEND_GUIDE:
        await send_guide(update, context)
    elif query.data == SHOW_ABOUT:
        await show_about(update, context)
    elif query.data == SHOW_APPOINTMENT:
        await show_appointment(update, context)
    elif query.data == SHOW_FAQ:
        await show_faq(update, context)
    else:
        await query.answer("Неизвестная команда")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с администратором."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("❌ No BOT_TOKEN found. Please set it in .env file")
        logger.error("Steps to fix:")
        logger.error("1. cp .env.example .env")
        logger.error("2. Edit .env and add your bot token from @BotFather")
        logger.error("3. Run: python bot.py")
        return
    
    logger.info("✓ BOT_TOKEN found")
    
    try:
        # Test imports
        logger.info("Testing imports...")
        from telegram import __version__ as telegram_version
        logger.info(f"✓ python-telegram-bot version: {telegram_version}")
        
        # Create Application
        logger.info("Creating Application...")
        application = Application.builder().token(token).build()
        logger.info("✓ Application created successfully")
        
        # Add handlers
        logger.info("Setting up handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("privacy", privacy_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                              handle_text))
        logger.info("✓ Handlers configured")
        
        # Add error handler
        application.add_error_handler(error_handler)
        logger.info("✓ Error handler added")
        
        # Start the bot
        logger.info("Starting polling...")
        application.run_polling()
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
