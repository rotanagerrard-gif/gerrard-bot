import os
from flask import Flask
import telebot

app = Flask(__name__)

BOT_TOKEN = "7508538976:AAE3hLX4371ptXLqFBT6W9QzEWdW2jl7WtQ"
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Bot is running 24/7!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ជម្រាបសួរ! 👋 ខ្ញុំជា Bot របស់បង រត់ 24/7 ពិតប្រាកដ។")

@bot.message_handler(func=lambda message: True)
def echo(message):
    text = message.text.lower()
    
    if "សួស្តី" in text or "hello" in text:
        bot.reply_to(message, "សួស្តី! 😊 តើខ្ញុំជួយអ្វីបានទេ?")
    elif "អរគុណ" in text or "thanks" in text:
        bot.reply_to(message, "មិនអីទេ! 🙏")
    else:
        bot.reply_to(message, f"បានទទួល: {message.text}")

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
