#6912849415:AAFsy-Bc7cQP3sbadUkBSrnIFlFKbwCa0L0
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext

# Bot token
TOKEN = '6912849415:AAFsy-Bc7cQP3sbadUkBSrnIFlFKbwCa0L0'

# Kanal ID (kanalingizning username ni @ belgisiz yozing, masalan, 'mychannel' uchun kanal ID @mychannel bo'ladi)
CHANNEL_USERNAME = 'try_motivation'

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# SQLite ma'lumotlar bazasini sozlash
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Jadvalni yaratish
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, invites INTEGER)''')
conn.commit()

# Har bir foydalanuvchi uchun unikal link yaratish uchun funksiya
def generate_unique_link(user_id):
    link = f'https://t.me/{CHANNEL_USERNAME}?start={user_id}'
    return link

# /start komandasi uchun handler
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = user.username
    
    # Foydalanuvchini bazaga qo'shish yoki yangilash
    c.execute('INSERT OR IGNORE INTO users (user_id, username, invites) VALUES (?, ?, ?)', (user_id, username, 0))
    conn.commit()

    user_link = generate_unique_link(user_id)
    await update.message.reply_text(f'Salom, kanalga qo\'shilish uchun quyidagi linkni bosing: {user_link}')

# Takliflar bilan ishlash uchun handler
async def handle_invite(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    
    # Taklif qilgan foydalanuvchi ID'sini olish
    if context.args:
        invited_by_id = int(context.args[0])
        
        if invited_by_id:
            # Taklif qilgan foydalanuvchiga ball qo'shish
            c.execute('UPDATE users SET invites = invites + 1 WHERE user_id = ?', (invited_by_id,))
            conn.commit()
            await update.message.reply_text(f'Taklif uchun rahmat!')

# /score komandasi uchun handler
async def score(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    
    # Foydalanuvchining ballarini olish
    c.execute('SELECT invites FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        invites = result[0]
        await update.message.reply_text(f'Sizda {invites} ball bor.')
    else:
        await update.message.reply_text('Siz hali hech kimni taklif qilmadingiz.')

# /leaderboard komandasi uchun handler
async def leaderboard(update: Update, context: CallbackContext):
    # Barcha foydalanuvchilarning ballarini olish va saralash
    c.execute('SELECT username, invites FROM users ORDER BY invites DESC')
    results = c.fetchall()
    
    if results:
        leaderboard_text = 'Umumiy natijalar jadvali:\n\n'
        for idx, (username, invites) in enumerate(results, start=1):
            leaderboard_text += f'{idx}. @{username}: {invites} ball\n'
        await update.message.reply_text(leaderboard_text)
    else:
        await update.message.reply_text('Hozircha hech qanday natija yo\'q.')

def main():
    # Application ni token bilan yarating
    application = Application.builder().token(TOKEN).build()

    # /start komandasi uchun handlerni ro'yxatdan o'tkazish
    application.add_handler(CommandHandler("start", start))
    # Taklifni qayta ishlash uchun handlerni ro'yxatdan o'tkazish
    application.add_handler(CommandHandler("invite", handle_invite))
    # /score komandasi uchun handlerni ro'yxatdan o'tkazish
    application.add_handler(CommandHandler("score", score))
    # /leaderboard komandasi uchun handlerni ro'yxatdan o'tkazish
    application.add_handler(CommandHandler("leaderboard", leaderboard))

    # Botni boshlash
    application.run_polling()

if __name__ == '__main__':
    main()
