import os
import logging
import json
import requests
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from flask import Flask, request
from telegram.ext import CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(_name_)

# Flask app
app = Flask(_name_)

# Telegram bot token
TOKEN = ("7477944602:AAFdaka8cEvi3fr-zXb9ke1azDTCQf9doiE")

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when /start command is issued"""
    update.message.reply_text("Hello! I can handle forwarded images and self-destructive ones.")

def handle_forwarded_photo(update: Update, context: CallbackContext) -> None:
    """Handle forwarded images (self-destruction or normal)"""
    if update.message.photo:
        # Get the photo file_id
        photo = update.message.photo[-1]  # The highest resolution photo
        file_id = photo.file_id

        # Download the image
        file = context.bot.get_file(file_id)
        file.download(f"photo_{file_id}.jpg")
        update.message.reply_text(f"Image saved: photo_{file_id}.jpg")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all other messages (non-photo)"""
    if update.message.text:
        update.message.reply_text("I'm here to help you handle forwarded photos.")

# Webhook handler
@app.route('/webhook', methods=['POST'])
def webhook():
    """This function will process incoming updates from Telegram"""
    if request.method == "POST":
        payload = request.get_data().decode("UTF-8")
        json_payload = json.loads(payload)

        # Get the Telegram update and pass it to the dispatcher
        update = Update.de_json(json_payload, context.bot)
        dispatcher.process_update(update)

        return 'ok', 200
    return "Invalid Request", 400

if _name_ == '_main_':
    # Set up the Updater and Dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.forwarded & Filters.photo, handle_forwarded_photo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start polling for updates (for testing locally)
    updater.start_polling()

    # Set up webhook route for Vercel
    app.run(host="0.0.0.0", port=5000)
