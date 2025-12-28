
import telebot
from telebot import types
import yt_dlp
import os
import threading
import time

import os
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# Хранение данных
users_downloads = {}
paid_users = set()

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Скачать видео", "ℹ️ Help")
    bot.send_message(
        message.chat.id,
        "👋 Привет!\n"
        "Я помогу скачать видео с Pinterest.\n\n"
        "🎁 Бесплатно: 3 скачивания",
        reply_markup=markup
    )

# ====== HELP ======
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ Помощь:\n\n"
        "📥 Нажми «Скачать видео»\n"
        "🔗 Отправь ссылку на Pinterest-видео\n\n"
        "🎁 3 скачивания бесплатно\n"
        "💳 Далее — подписка\n\n"
        "Поддержка: @your_username"
    )

# ====== SUBSCRIBE ======
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    bot.send_message(
        message.chat.id,
        "💳 Подписка:\n\n"
        "1 месяц — 5 000 сум\n\n"
        "Для оплаты напиши админу:\n"
        "@your_username"
    )

# ====== DOWNLOAD ======
@bot.message_handler(func=lambda m: True)
def download_pinterest(message):
    user_id = message.chat.id
    text = message.text

    if text == "📥 Скачать видео":
        bot.send_message(user_id, "🔗 Отправь ссылку на видео из Pinterest")
        return

    if text == "ℹ️ Help":
        help_cmd(message)
        return

    if not text.startswith("http"):
        bot.send_message(user_id, "❌ Отправь корректную ссылку")
        return

    if user_id not in users_downloads:
        users_downloads[user_id] = 0

    if user_id not in paid_users and users_downloads[user_id] >= 3:
        bot.send_message(
            user_id,
            "❌ Лимит бесплатных скачиваний исчерпан.\n"
            "💳 Купи подписку: /subscribe"
        )
        return

    bot.send_message(user_id, "⏳ Скачиваю видео...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        for file in os.listdir():
            if file.startswith("video"):
                with open(file, 'rb') as v:
                    bot.send_video(user_id, v)
                os.remove(file)
                users_downloads[user_id] += 1
                break

    except Exception:
        bot.send_message(user_id, "❌ Ошибка. Проверь ссылку.")

# ====== ADS EVERY 3 DAYS ======
def ads():
    while True:
        time.sleep(259200)  # 3 дня
        for user in users_downloads.keys():
            try:
                bot.send_message(
                    user,
                    "📢 Реклама:\n"
                    "Нужен бот или сайт? Пиши @your_username"
                )
            except:
                pass

threading.Thread(target=ads).start()

# ====== RUN ======
print("БОТ ЗАПУЩЕН")
bot.polling()


