import os
import logging
import json
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot token
TOKEN = "7477944602:AAFdaka8cEvi3fr-zXb9ke1azDTCQf9doiE"

# Set up the Updater and Dispatcher
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when /start command is issued"""
    update.message.reply_text("Hello! Send me a forwarded photo, and I’ll handle it.")

def handle_forwarded_photo(update: Update, context: CallbackContext) -> None:
    """Handle forwarded images (normal & self-destruct)"""
    if update.message.photo:
        # Get the photo file_id
        photo = update.message.photo[-1]  # The highest resolution photo
        file_id = photo.file_id

        # Download the image
        file = context.bot.get_file(file_id)
        file.download(f"photo_{file_id}.jpg")
        
        update.message.reply_text(f"Image saved: photo_{file_id}.jpg")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle non-photo messages"""
    update.message.reply_text("Send me a forwarded photo!")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Process incoming updates from Telegram via webhook"""
    if request.method == "POST":
        payload = request.get_data().decode("UTF-8")
        json_payload = json.loads(payload)
        update = Update.de_json(json_payload, updater.bot)
        dispatcher.process_update(update)
        return 'ok', 200
    return "Invalid Request", 400

if __name__ == '__main__':
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.forwarded & Filters.photo, handle_forwarded_photo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start polling (for local testing)
    updater.start_polling()

    # Uncomment below if using webhook
    # updater.bot.setWebhook("https://your-deployed-app.com/webhook")

    # Start Flask app
    app.run(host="0.0.0.0", port=5000)
