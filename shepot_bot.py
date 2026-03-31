"""
🤫 Бот для плагина "Шепот" (Exteragram)
========================================
Установка:
    pip install pyTelegramBotAPI

Запуск:
    python shepot_bot.py

Получи токен у @BotFather и вставь ниже.
"""

import base64
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ╔══════════════════════════════════════════════════╗
# ║  ВСТАВЬ ТОКЕН БОТА от @BotFather                ║
# ╚══════════════════════════════════════════════════╝
BOT_TOKEN = "ВСТАВЬ_ТОКЕН_СЮДА"

bot = telebot.TeleBot(BOT_TOKEN)

# ── Смешные цитаты для чужаков ────────────────────────────────────────────────
FORBIDDEN_QUOTES = [
    "🙈 Шепот — не для твоих ушей, дружище. Иди займись своими делами!",
    "🦜 Попугай тоже хочет знать чужие секреты. Попугаю тоже не говорят.",
    "🔐 Этот шепот защищён силой древних магов и одной строчкой кода.",
    "🕵️ Агент 007 пытался взломать этот шепот. Провалился. Ты — тоже.",
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
    "🪐 На Марсе разрешили бы тебе слушать чужие шепоты. Но ты не на Марсе.",
]


def decode_secret(encoded: str) -> str | None:
    """Декодирует base64-строку обратно в текст."""
    try:
        # Добавляем padding если нужно
        padding = 4 - len(encoded) % 4
        if padding != 4:
            encoded += "=" * padding
        return base64.b64decode(encoded.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def parse_callback_data(data: str) -> tuple[str, str, str] | None:
    """
    Формат: s|sender|target|encoded_message
    Возвращает (sender, target, secret_text) или None при ошибке.
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


# ── /start ────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(
        message,
        "🤫 *Бот Шепота*\n\n"
        "Я работаю в паре с плагином *Шепот* для Exteragram.\n\n"
        "Используй команду в чате:\n"
        "`.шепот @username секретный текст`\n\n"
        "Только адресат увидит содержимое шепота!",
        parse_mode="Markdown"
    )


# ── Обработчик inline-кнопки ─────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data.startswith("s|"))
def handle_whisper_button(call):
    parsed = parse_callback_data(call.data)

    if parsed is None:
        bot.answer_callback_query(
            call.id,
            text="❌ Шепот повреждён или уже недоступен.",
            show_alert=True
        )
        return

    sender, target, secret_text = parsed

    # Получаем username того, кто нажал кнопку
    clicker = call.from_user
    clicker_username = (clicker.username or "").lower().strip()
    target_clean = target.lower().strip().lstrip("@")
    sender_clean = sender.lower().strip().lstrip("@")

    # Адресат или отправитель могут читать шепот
    is_allowed = (
        clicker_username == target_clean
        or clicker_username == sender_clean
    )

    if is_allowed:
        # Показываем шепот
        bot.answer_callback_query(
            call.id,
            text=f"🤫 {secret_text}",
            show_alert=True
        )
    else:
        # Показываем рандомную смешную цитату
        quote = random.choice(FORBIDDEN_QUOTES)
        bot.answer_callback_query(
            call.id,
            text=quote,
            show_alert=True
        )


# ── Запуск ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤫 Бот Шепота запущен...")
    print(f"   Бот: @{bot.get_me().username}")
    print("   Ожидаю нажатия кнопок...")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
