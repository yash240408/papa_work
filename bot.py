import os
import logging
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, request

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot token
TOKEN = "7477944602:AAFdaka8cEvi3fr-zXb9ke1azDTCQf9doiE"

# Create application
app_telegram = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when /start command is issued"""
    print("Hello! Send me a forwarded photo, and I’ll handle it.")
    await update.message.reply_text("Hello! Send me a forwarded photo, and I’ll handle it.")

async def handle_forwarded_photo(update: Update, context: CallbackContext) -> None:
    """Handle forwarded images (normal & self-destruct)"""
    if update.message.photo:
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        file_id = photo.file_id

        # Download the image
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(f"photo_{file_id}.jpg")
        print(f"Image saved: photo_{file_id}.jpg")
        await update.message.reply_text(f"Image saved: photo_{file_id}.jpg")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle non-photo messages"""
    print("Send me a forwarded photo!")
    await update.message.reply_text("Send me a forwarded photo!")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Process incoming updates from Telegram via webhook"""
    if request.method == "POST":
        payload = request.get_data().decode("UTF-8")
        json_payload = json.loads(payload)
        update = Update.de_json(json_payload, app_telegram.bot)
        app_telegram.update_queue.put_nowait(update)
        return 'ok', 200
    return "Invalid Request", 400

if __name__ == '__main__':
    # Add handlers
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.FORWARDED & filters.PHOTO, handle_forwarded_photo))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling (for local testing)
    app_telegram.run_polling()

    # Uncomment below if using webhook
    # app_telegram.bot.setWebhook("https://your-deployed-app.com/webhook")

    # Start Flask app
    app.run(host="0.0.0.0", port=5000)
