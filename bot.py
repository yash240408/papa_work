import os
import logging
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import Dispatcher

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(_name_)

# Your bot token here
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello, this is your bot!")

# Define the function to handle the webhook (HTTP request)
def handler(request):
    if request.method == "POST":
        # Get the request payload
        payload = json.loads(request.data)

        # Set up the Updater and Dispatcher with the bot token
        updater = Updater(TOKEN)
        dispatcher = updater.dispatcher
        
        # Handle incoming messages
        dispatcher.add_handler(CommandHandler("start", start))

        # Process the incoming update
        updater.process_update(Update.de_json(payload, updater.bot))
        return json.dumps({"message": "success"}), 200
    return "Invalid Request", 400
