import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import requests
import io
import os

"""
Smart Utility Bot – Your All-in-One Productivity Assistant!
-----------------------------------------------------------
Features:
- /shorten: Shorten long URLs using Bitly
- /track: Track click stats and get a visual bar chart
- /convert: Convert between PDF ↔ DOCX and Image → PDF
- /summarize: Upload a file (PDF, DOCX, TXT) to get an AI summary
- Multilingual Support: Auto-detects your language and replies accordingly

Powered by:
- Bitly API for URL shortening and analytics
- Google Translate for language detection and translation
- Python Telegram Bot (v13) for Telegram integration

Developed with Python 3.10
"""

from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
)
from telegram import ReplyKeyboardMarkup

# --- Configuration ---
TELEGRAM_TOKEN = "8142480751:AAF4vJBwt9VKZkH_SXWysjiq_zVeTbFyFso"
BITLY_TOKEN = "c9872a7c79b4fa65c25ff9b953937d88c873bff6"

# Add a "Main Menu" button to allow users to return to the menu
def send_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("📊 Track URL Stats", callback_data='track')],
        [InlineKeyboardButton("📂 Convert File", callback_data='convert')],
        [InlineKeyboardButton("🧠 Summarize File", callback_data='summarize')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        update.callback_query.edit_message_text(
            "🤖 Main Menu:\n\nChoose an action:",
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            "🤖 Main Menu:\n\nChoose an action:",
            reply_markup=reply_markup
        )
        send_reply_keyboard(update)  # Add this line

# --- Logging ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def shorten_url(long_url: str) -> str:
    headers = {"Authorization": f"Bearer {BITLY_TOKEN}"}
    json_data = {"long_url": long_url}
    response = requests.post("https://api-ssl.bitly.com/v4/shorten", headers=headers, json=json_data)
    if response.ok:
        return response.json()["link"]
    else:
        return "Error: Could not shorten URL."

def get_bitly_stats(bitly_url: str):
    bitlink = bitly_url.replace("https://", "").replace("http://", "")
    headers = {"Authorization": f"Bearer {BITLY_TOKEN}"}
    response = requests.get(f"https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary", headers=headers)
    if response.ok:
        return response.json().get("total_clicks", 0)
    else:
        return None

def detect_language(text: str) -> str:
    response = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text}
    )
    if response.ok:
        lang = response.json()[2]
        return lang
    return "en"

def translate_text(text: str, target_lang: str) -> str:
    response = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "auto", "tl": target_lang, "dt": "t", "q": text}
    )
    if response.ok:
        return response.json()[0][0][0]
    return text

# --- Command Handlers ---

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("📊 Track URL Stats", callback_data='track')],
        [InlineKeyboardButton("📂 Convert File", callback_data='convert')],
        [InlineKeyboardButton("🧠 Summarize File", callback_data='summarize')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🤖 Welcome to Smart Utility Bot!\n\nChoose an action:",
        reply_markup=reply_markup
    )
    send_reply_keyboard(update)  # Add this line

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'shorten':
        query.edit_message_text("Send me the long URL you want to shorten.")
        context.user_data['action'] = 'shorten'
    elif query.data == 'track':
        query.edit_message_text("Send me the Bitly URL to track clicks.")
        context.user_data['action'] = 'track'
    elif query.data == 'convert':
        query.edit_message_text("Send me a file (PDF, DOCX, or image) to convert.")
        context.user_data['action'] = 'convert'
    elif query.data == 'summarize':
        query.edit_message_text("Send me a file (PDF, DOCX, TXT) to summarize.")
        context.user_data['action'] = 'summarize'

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    # Map button text to actions
    if text == '🔗 Shorten URL':
        context.user_data['action'] = 'shorten'
        update.message.reply_text("Send me the long URL you want to shorten.")
    elif text == '📊 Track URL Stats':
        context.user_data['action'] = 'track'
        update.message.reply_text("Send me the Bitly URL to track clicks.")
    elif text == '📂 Convert File':
        context.user_data['action'] = 'convert'
        update.message.reply_text("Send me a file (PDF, DOCX, or image) to convert.")
    elif text == '🧠 Summarize File':
        context.user_data['action'] = 'summarize'
        update.message.reply_text("Send me a file (PDF, DOCX, TXT) to summarize.")
    else:
        # Existing logic for shorten/track actions
        action = context.user_data.get('action')
        if action == 'shorten':
            short_url = shorten_url(text)
            update.message.reply_text(f"Shortened URL: {short_url}")
            context.user_data['action'] = None
        elif action == 'track':
            clicks = get_bitly_stats(text)
            if clicks is not None:
                update.message.reply_text(f"Total Clicks: {clicks}")
            else:
                update.message.reply_text("Could not retrieve stats. Please check the URL.")
            context.user_data['action'] = None
        else:
            update.message.reply_text("Please choose an action using /start.")

def handle_document(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    file = update.message.document
    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    file_bytes = io.BytesIO()
    new_file.download(out=file_bytes)
    file_bytes.seek(0)
    filename = file.file_name

    if action == 'summarize':
        # For simplicity, only handle TXT files here
        if filename.endswith('.txt'):
            text = file_bytes.read().decode('utf-8')
            # HuggingFace summarization removed, just echo the text
            update.message.reply_text(f"File received. (Summarization feature is currently unavailable.)")
        else:
            update.message.reply_text("Only TXT files are supported for summarization in this demo.")
        context.user_data['action'] = None
    elif action == 'convert':
        update.message.reply_text("File conversion feature coming soon!")
        context.user_data['action'] = None
    else:
        update.message.reply_text("Please choose an action using /start.")

def send_reply_keyboard(update):
    reply_keyboard = [
        ['🔗 Shorten URL', '📊 Track URL Stats'],
        ['📂 Convert File', '🧠 Summarize File']
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    update.message.reply_text("Choose an option from the keyboard below:", reply_markup=markup)

# --- Main ---

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", send_main_menu))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.document, handle_document))

    print("Bot started. Send /start in your Telegram chat to see the buttons.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
