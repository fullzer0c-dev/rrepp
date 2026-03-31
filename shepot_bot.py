"""
🤫 Бот Шепота — финальная версия для Render
============================================
Файлы для GitHub:
  - shepot_bot.py     (этот файл)
  - requirements.txt  (pyTelegramBotAPI + flask)
"""

import base64
import random
import threading
import os

import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ╔══════════════════════════════════════════════════╗
# ║  Вставь токен бота от @BotFather                ║
# ╚══════════════════════════════════════════════════╝
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618276737:AAH1hVvquZMH14or2WRU-DwOnp6ZpMorGxQ")

bot = telebot.TeleBot(BOT_TOKEN)

# ── Flask-сервер чтобы Render не засыпал ─────────────────────────────────────
app = Flask(__name__)

@app.route("/")
def index():
    return "🤫 Бот Шепота работает!", 200

@app.route("/health")
def health():
    return "ok", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ── Смешные цитаты для чужаков ────────────────────────────────────────────────
FORBIDDEN_QUOTES = [
    "🙈 Шепот — не для твоих ушей, дружище. Иди займись своими делами!",
    "🦜 Попугай тоже хочет знать чужие секреты. Попугаю тоже не говорят.",
    "🔐 Этот шепот защищён силой древних магов и одной строчкой кода.",
    "🕵️ Агент 007 пытался взломать этот шепот. Провалился. Ты тоже.",
    "🍕 За подслушивание чужих шепотов полагается лишение пиццы на 3 недели.",
    "🐉 Дракон охраняет этот шепот. Дракон сыт, но принципиален.",
    "👻 Призрак Неизданных Секретов смотрит на тебя с разочарованием.",
    "🎭 Это не твой шепот. Чужой шепот — как чужой борщ. Не трогай.",
    "🚀 NASA засекретило этот шепот в 1969 году. Совпадение? Не думаю.",
    "🐙 Осьминог знает всё, но не расскажет. Ты — даже не осьминог.",
    "🧙 Гэндальф говорит: 'Ты не пройдёшь!' И он прав насчёт этого шепота.",
    "🎪 Добро пожаловать в цирк чужих секретов! Вход только для адресата.",
    "🦄 Единорог мог бы рассказать тебе этот шепот... Но единорогов не существует.",
    "🍄 Гриб говорит: чужие шепоты как грибы в лесу — не каждый для тебя.",
    "🎸 Этот шепот — как эксклюзивный концерт. Твоего билета здесь нет, братан.",
    "🌚 Луна слышала этот шепот. Луна молчит. Бери пример с Луны.",
    "🐈 Кот знает все тайны мира, но выдаёт их только адресату. Ты — не адресат.",
    "🎩 Фокусник исчез бы с этим шепотом. Ты, к сожалению, не фокусник.",
    "🧊 Шепот заморожен в криоскладе секретов. Доступ — только для посвящённых.",
    "🪐 На Марсе разрешили бы слушать чужие шепоты. Но ты не на Марсе.",
]


# ── Утилиты ───────────────────────────────────────────────────────────────────

def decode_secret(encoded: str) -> str | None:
    try:
        padding = 4 - len(encoded) % 4
        if padding != 4:
            encoded += "=" * padding
        return base64.b64decode(encoded.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def parse_callback(data: str):
    """
    Формат callback_data: s|sender|target|base64_message
    Возвращает (sender, target, secret) или None.
    """
    try:
        parts = data.split("|", 3)
        if len(parts) != 4 or parts[0] != "s":
            return None
        _, sender, target, encoded = parts
        secret = decode_secret(encoded)
        if secret is None:
            return None
        return sender, target, secret
    except Exception:
        return None


# ── Команды бота ─────────────────────────────────────────────────────────────

@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    bot.reply_to(
        message,
        "🤫 *Бот Шепота*\n\n"
        "Работает в паре с плагином *Шепот* для Exteragram.\n\n"
        "Как использовать в чате:\n"
        "`.шепот @username секретный текст`\n\n"
        "Только отправитель и адресат увидят шепот.\n"
        "Все остальные получат смешную отговорку 😄",
        parse_mode="Markdown"
    )


# ── Обработчик кнопки ─────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: call.data.startswith("s|"))
def handle_whisper(call):
    parsed = parse_callback(call.data)

    if parsed is None:
        bot.answer_callback_query(
            call.id,
            text="❌ Шепот повреждён или недоступен.",
            show_alert=True
        )
        return

    sender, target, secret = parsed
    clicker = (call.from_user.username or "").lower().strip()
    sender_clean = sender.lower().strip()
    target_clean = target.lower().strip()

    # Отправитель и адресат читают шепот
    if clicker in (sender_clean, target_clean):
        bot.answer_callback_query(
            call.id,
            text=f"🤫 {secret}",
            show_alert=True
        )
    else:
        # Все остальные — рандомная цитата
        bot.answer_callback_query(
            call.id,
            text=random.choice(FORBIDDEN_QUOTES),
            show_alert=True
        )


# ── Запуск ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🤫 Запуск бота @{bot.get_me().username}...")

    # Flask в отдельном потоке — держит Render живым
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Flask запущен, Render не заснёт.")

    # Бот в основном потоке
    print("📡 Polling запущен...")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
