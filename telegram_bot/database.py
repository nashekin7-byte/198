import sqlite3
import logging
import os
from datetime import datetime
from contextlib import contextmanager

# Определение путей относительно расположения файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bot_data', 'bot.db')
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'bot.log')

# Создание директорий, если они не существуют
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_PATH,
    filemode='a'
)

@contextmanager
def db_session():
    """Контекстный менеджер для работы с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Инициализация БД (создание таблицы если её нет)."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    paid BOOLEAN DEFAULT 0,
                    paid_date TIMESTAMP,
                    materials_sent BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

def add_user(user_id, username, first_name):
    """Добавление нового пользователя."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (user_id, username, first_name) 
                            VALUES (?, ?, ?)''', (user_id, username, first_name))
            conn.commit()
            logging.info(f"User {user_id} added to database")
    except sqlite3.IntegrityError:
        logging.warning(f"User {user_id} already exists")
    except Exception as e:
        logging.error(f"Database error in add_user: {e}")

def user_exists(user_id):
    """Проверка существования пользователя."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone() is not None
            logging.debug(f"Checked existence for user {user_id}: {exists}")
            return exists
    except Exception as e:
        logging.error(f"Database error in user_exists: {e}")
        return False

def get_user_info(user_id):
    """Получить всю информацию о пользователе."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                logging.debug(f"Retrieved info for user {user_id}")
                return dict(row)
            logging.debug(f"User {user_id} not found")
            return None
    except Exception as e:
        logging.error(f"Database error in get_user_info: {e}")
        return None

def check_user_paid(user_id):
    """Проверка оплаты пользователя."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT paid FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                paid = bool(row['paid'])
                logging.debug(f"Checked payment for user {user_id}: {paid}")
                return paid
            return False
    except Exception as e:
        logging.error(f"Database error in check_user_paid: {e}")
        return False

def mark_user_paid(user_id):
    """Отметить пользователя как оплатившего."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            paid_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE users SET paid = 1, paid_date = ? WHERE user_id = ?', 
                         (paid_date, user_id))
            conn.commit()
            logging.info(f"User {user_id} marked as paid")
    except Exception as e:
        logging.error(f"Database error in mark_user_paid: {e}")

def check_materials_sent(user_id):
    """Проверка отправки материалов."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT materials_sent FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                sent = bool(row['materials_sent'])
                logging.debug(f"Checked materials for user {user_id}: {sent}")
                return sent
            return False
    except Exception as e:
        logging.error(f"Database error in check_materials_sent: {e}")
        return False

def mark_materials_sent(user_id):
    """Отметить материалы как отправленные."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET materials_sent = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            logging.info(f"Materials marked as sent for user {user_id}")
    except Exception as e:
        logging.error(f"Database error in mark_materials_sent: {e}")

def get_all_users():
    """Получить список всех пользователей."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            users = [dict(row) for row in rows]
            logging.debug(f"Retrieved all users, count: {len(users)}")
            return users
    except Exception as e:
        logging.error(f"Database error in get_all_users: {e}")
        return []

def get_paid_users():
    """Получить ID всех оплативших."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE paid = 1')
            rows = cursor.fetchall()
            user_ids = [row['user_id'] for row in rows]
            logging.debug(f"Retrieved paid user IDs, count: {len(user_ids)}")
            return user_ids
    except Exception as e:
        logging.error(f"Database error in get_paid_users: {e}")
        return []

def get_paid_users_count():
    """Количество оплативших пользователей."""
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE paid = 1')
            row = cursor.fetchone()
            count = row['count'] if row else 0
            logging.debug(f"Paid users count: {count}")
            return count
    except Exception as e:
        logging.error(f"Database error in get_paid_users_count: {e}")
        return 0

if __name__ == "__main__":
    # Инициализация при запуске файла
    init_db()
