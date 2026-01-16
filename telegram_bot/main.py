import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from database import (
    init_db,
    add_user,
    check_user_paid,
    check_materials_sent,
    user_exists,
    get_user_info,
    mark_materials_sent,
    get_all_users,
    get_paid_users,
    get_paid_users_count,
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

# Состояния для ConversationHandler
(WAITING_USER_ID, WAITING_MATERIAL, WAITING_BROADCAST) = range(3)

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
    elif text == "💰 Отметить оплату":
        # Будет реализовано в Задаче 7
        pass
    # "📤 Отправить материал" и "📢 Рассылка всем" обрабатываются через ConversationHandler

# ConversationHandler functions for sending materials
async def send_material_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса отправки материала"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_admin(user_id):
        return ConversationHandler.END

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "📤 ОТПРАВКА МАТЕРИАЛА\n\n"
                "Введите ID клиента (можно скопировать из списка):\n\n"
                "Используйте команду /cancel для отмены"
            )
        )

        logger.info(f"Admin {user_id} started send material process")
        return WAITING_USER_ID

    except Exception as e:
        logger.error(f"Error in send_material_start: {e}")
        await context.bot.send_message(chat_id=chat_id, text="❌ Произошла ошибка")
        return ConversationHandler.END

async def send_material_get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получить ID клиента"""
    admin_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        user_id_str = update.message.text.strip()

        # Проверить, что это число
        try:
            target_user_id = int(user_id_str)
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Неверный формат ID. ID должен быть числом.\n\n"
                    "Попробуйте ещё раз или используйте /cancel для отмены"
                )
            )
            return WAITING_USER_ID

        # Проверить существование пользователя
        if not user_exists(target_user_id):
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"❌ Клиент с ID `{target_user_id}` не найден.\n\n"
                    "Проверьте ID и попробуйте ещё раз или используйте /cancel для отмены"
                ),
                parse_mode='Markdown'
            )
            return WAITING_USER_ID

        # Получить информацию о клиенте
        user_info = get_user_info(target_user_id)

        if not user_info:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Не удалось получить информацию о клиенте"
            )
            return WAITING_USER_ID

        # Сохранить ID в контексте
        context.user_data['target_user_id'] = target_user_id
        context.user_data['target_user_info'] = user_info

        # Показать информацию о клиенте
        client_info_text = (
            "✅ Клиент найден:\n\n"
            f"ID: `{user_info['user_id']}`\n"
            f"Имя: {user_info['first_name']}\n"
            f"Username: @{user_info['username']}\n"
            f"Оплата: {'✅ Да' if user_info['paid'] else '❌ Нет'}\n"
            f"Материалы: {'✅ Отправлены' if user_info['materials_sent'] else '⏳ Не отправлены'}\n\n"
            "Теперь отправьте материал (фото, видео, документ или текст):"
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=client_info_text,
            parse_mode='Markdown'
        )

        logger.info(f"Admin {admin_id} selected target user {target_user_id}")
        return WAITING_MATERIAL

    except Exception as e:
        logger.error(f"Error in send_material_get_user_id: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при обработке ID"
        )
        return ConversationHandler.END

async def send_material_get_material(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получить материал и отправить клиенту"""
    admin_id = update.effective_user.id
    admin_chat_id = update.effective_chat.id

    try:
        target_user_id = context.user_data.get('target_user_id')
        target_user_info = context.user_data.get('target_user_info')

        if not target_user_id:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text="❌ Ошибка: информация о клиенте потеряна"
            )
            return ConversationHandler.END

        # Определить тип материала
        material_type = None
        material_file_id = None

        if update.message.photo:
            material_type = "фото"
            material_file_id = update.message.photo[-1].file_id  # Берём самое высокое разрешение
        elif update.message.video:
            material_type = "видео"
            material_file_id = update.message.video.file_id
        elif update.message.document:
            material_type = "документ"
            material_file_id = update.message.document.file_id
        elif update.message.text:
            material_type = "текст"
        else:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=(
                    "❌ Неподдерживаемый тип файла. "
                    "Отправьте фото, видео, документ или текст."
                )
            )
            return WAITING_MATERIAL

        # Отправить материал клиенту
        try:
            emoji_map = {
                "фото": "📸",
                "видео": "🎥",
                "документ": "📄",
                "текст": "📝"
            }
            emoji = emoji_map.get(material_type, "📦")

            caption = f"{emoji} Ваши материалы:"

            if material_type == "фото":
                await context.bot.send_photo(
                    chat_id=target_user_id,
                    photo=material_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif material_type == "видео":
                await context.bot.send_video(
                    chat_id=target_user_id,
                    video=material_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif material_type == "документ":
                await context.bot.send_document(
                    chat_id=target_user_id,
                    document=material_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif material_type == "текст":
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"{caption}\n\n{update.message.text}"
                )

            # Отметить в БД что материалы отправлены
            mark_materials_sent(target_user_id)

            # Подтвердить админу
            confirmation_text = (
                f"✅ Материал ({material_type}) отправлен клиенту "
                f"{target_user_info['first_name']} (ID: `{target_user_id}`)\n\n"
                "Используйте /admin для возврата в админ-панель"
            )

            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=confirmation_text,
                parse_mode='Markdown'
            )

            logger.info(
                f"Admin {admin_id} sent {material_type} material to user {target_user_id}"
            )

        except Exception as send_error:
            # Если клиент заблокировал бота или другая ошибка
            if "blocked" in str(send_error).lower() or "user is deactivated" in str(send_error).lower():
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=(
                        f"❌ Не удалось отправить материал клиенту {target_user_info['first_name']}.\n\n"
                        "Возможно, клиент заблокировал бота или удалил аккаунт."
                    )
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=f"❌ Ошибка при отправке материала: {str(send_error)}"
                )

            logger.error(f"Error sending material to user {target_user_id}: {send_error}")
            return ConversationHandler.END

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in send_material_get_material: {e}")
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text="❌ Произошла ошибка при обработке материала"
        )
        return ConversationHandler.END

async def cancel_send_material(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена отправки материала"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "❌ Отправка материала отменена.\n\n"
                "Используйте /admin для возврата в админ-панель"
            )
        )

        logger.info(f"Admin {user_id} cancelled send material operation")

    except Exception as e:
        logger.error(f"Error in cancel_send_material: {e}")

    return ConversationHandler.END

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса рассылки материалов всем оплатившим клиентам"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    try:
        # Получить количество оплативших
        paid_count = get_paid_users_count()
        
        if paid_count == 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Нет оплативших клиентов для рассылки"
            )
            return ConversationHandler.END
        
        broadcast_text = (
            "📢 РАССЫЛКА МАТЕРИАЛА ВСЕМ ОПЛАТИВШИМ КЛИЕНТАМ\n\n"
            f"Получат: {paid_count} человек(а)\n\n"
            "Отправьте материал для рассылки (фото, видео, документ или текст):\n\n"
            "Используйте команду /cancel для отмены"
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=broadcast_text
        )
        
        logger.info(f"Admin {user_id} started broadcast to {paid_count} users")
        return WAITING_BROADCAST
        
    except Exception as e:
        logger.error(f"Error in broadcast_start: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при инициализации рассылки"
        )
        return ConversationHandler.END

async def broadcast_send_material(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получить материал и отправить всем оплатившим клиентам"""
    admin_id = update.effective_user.id
    admin_chat_id = update.effective_chat.id
    
    try:
        # Определить тип материала
        material_type = None
        material_file_id = None
        caption_emoji = "📦"
        
        if update.message.photo:
            material_type = "фото"
            material_file_id = update.message.photo[-1].file_id
            caption_emoji = "📸"
        elif update.message.video:
            material_type = "видео"
            material_file_id = update.message.video.file_id
            caption_emoji = "🎥"
        elif update.message.document:
            material_type = "документ"
            material_file_id = update.message.document.file_id
            caption_emoji = "📄"
        elif update.message.text:
            material_type = "текст"
            caption_emoji = "📝"
        else:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=(
                    "❌ Неподдерживаемый тип файла. "
                    "Отправьте фото, видео, документ или текст."
                )
            )
            return WAITING_BROADCAST
        
        # Показать сообщение "Отправляю материалы..."
        progress_message = await context.bot.send_message(
            chat_id=admin_chat_id,
            text="⏳ Отправляю материалы..."
        )
        
        # Получить всех оплативших
        paid_users = get_paid_users()
        
        if not paid_users:
            await context.bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=progress_message.message_id,
                text="❌ Нет оплативших клиентов для рассылки"
            )
            return ConversationHandler.END
        
        # Отправить материал каждому
        successful_count = 0
        error_count = 0
        blocked_users = []
        
        caption = f"{caption_emoji} Новые материалы для вас:"
        
        for idx, target_user_id in enumerate(paid_users):
            try:
                # Отправить материал в зависимости от типа
                if material_type == "фото":
                    await context.bot.send_photo(
                        chat_id=target_user_id,
                        photo=material_file_id,
                        caption=caption,
                        parse_mode='HTML'
                    )
                elif material_type == "видео":
                    await context.bot.send_video(
                        chat_id=target_user_id,
                        video=material_file_id,
                        caption=caption,
                        parse_mode='HTML'
                    )
                elif material_type == "документ":
                    await context.bot.send_document(
                        chat_id=target_user_id,
                        document=material_file_id,
                        caption=caption,
                        parse_mode='HTML'
                    )
                elif material_type == "текст":
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"{caption}\n\n{update.message.text}"
                    )
                
                successful_count += 1
                
                # Обновить прогресс (каждый 5-й пользователь)
                if (idx + 1) % 5 == 0:
                    await context.bot.edit_message_text(
                        chat_id=admin_chat_id,
                        message_id=progress_message.message_id,
                        text=f"⏳ Отправляю материалы... ({idx + 1}/{len(paid_users)})"
                    )
                
            except Exception as send_error:
                error_count += 1
                error_msg = str(send_error).lower()
                
                # Проверить тип ошибки
                if "blocked" in error_msg or "user is deactivated" in error_msg:
                    blocked_users.append(target_user_id)
                    logger.warning(f"User {target_user_id} blocked the bot")
                else:
                    logger.error(f"Error sending to user {target_user_id}: {send_error}")
            
            # Добавить задержку (0.05 сек) чтобы не упереться в лимиты Telegram
            import asyncio
            await asyncio.sleep(0.05)
        
        # Удалить сообщение "Отправляю материалы..."
        try:
            await context.bot.delete_message(
                chat_id=admin_chat_id,
                message_id=progress_message.message_id
            )
        except:
            pass
        
        # Показать статистику
        stats_text = (
            f"✅ Рассылка завершена!\n\n"
            f"📊 Статистика:\n"
            f"✅ Успешно: {successful_count}\n"
            f"❌ Ошибок: {error_count}"
        )
        
        if blocked_users:
            stats_text += f"\n🚫 Заблокировали: {len(blocked_users)}"
        
        stats_text += (
            f"\n\nИтого получили: {successful_count}/{len(paid_users)}\n\n"
            "Используйте /admin для возврата в админ-панель"
        )
        
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text=stats_text
        )
        
        logger.info(
            f"Admin {admin_id} completed broadcast: "
            f"sent to {successful_count}, errors: {error_count}, blocked: {len(blocked_users)}"
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in broadcast_send_material: {e}")
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text="❌ Произошла ошибка при отправке материалов"
        )
        return ConversationHandler.END

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена рассылки"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "❌ Рассылка отменена.\n\n"
                "Используйте /admin для возврата в админ-панель"
            )
        )
        
        logger.info(f"Admin {user_id} cancelled broadcast operation")
        
    except Exception as e:
        logger.error(f"Error in cancel_broadcast: {e}")
    
    return ConversationHandler.END

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

    # ConversationHandler для рассылки материалов
    broadcast_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^📢 Рассылка всем$"), broadcast_start)],
        states={
            WAITING_BROADCAST: [
                MessageHandler(
                    filters.PHOTO | filters.VIDEO | filters.Document.PDF | filters.TEXT,
                    broadcast_send_material
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_broadcast)],
    )

    app.add_handler(broadcast_handler)

    # Запустить бота
    logger.info("Bot started polling")
    app.run_polling()

if __name__ == "__main__":
    main()
