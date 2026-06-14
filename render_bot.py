import os
from flask import Flask
import telebot

# បង្កើត Web Server ជាមួយ Flask សម្រាប់ Render ឆែកមើល (Health Check)
app = Flask(__name__)

# ដាក់ Token របស់បងចូលរួចរាល់
BOT_TOKEN = "7508538976:AAE3hLX4371ptXLqFBT6W9QzEWdW2jl7WtQ"
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Bot is running 24/7!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ជម្រាបសួរលោកបង! ខ្ញុំជា Bot របស់បង ដែលរត់នៅលើ Render ២4 ម៉ោងពិតប្រាកដ។")

# បន្ថែមមុខងារកូដផ្សេងៗទៀត (ដូចជាកូដទាញយកវីដេអូ) នៅខាងក្រោមនេះ...

if __name__ == "__main__":
    # បើកឱ្យ Bot ដំណើរការ Background
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    # បើក Web Server ឱ្យ Render ចាប់ Signal
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
