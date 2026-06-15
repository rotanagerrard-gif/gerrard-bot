import os
import glob
import subprocess
from time import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# 🔐 Token របស់អ្នក
BOT_TOKEN = "7508538976:AAE3hLX4371ptXLqFBT6W9QzEWdW2jl7WtQ"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

ADMIN_ID = 7097515717
user_links = {}

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(
        m,
        "👋 សួស្តី!\n"
        "📩 ផ្ញើលីង YouTube ឬ TikTok មកទីនេះដើម្បីទាញយក\n"
        "📌 /report [សារ] ដើម្បីរាយការណ៍ទៅ Admin"
    )

# ---------------- UPDATE (ADMIN ONLY) ----------------
@bot.message_handler(commands=['update'])
def update_bot(m):
    if m.from_user.id != ADMIN_ID:
        return

    msg = bot.reply_to(m, "⏳ កំពុង Update yt-dlp...")
    try:
        subprocess.check_call(["pip", "install", "-U", "yt_dlp"])
        bot.edit_message_text("✅ Update ជោគជ័យ!", m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ បរាជ័យ: {e}", m.chat.id, msg.message_id)

# ---------------- REPORT ----------------
@bot.message_handler(commands=['report'])
def report(m):
    parts = m.text.split(" ", 1)

    if len(parts) < 2:
        bot.reply_to(m, "❌ ប្រើ៖ /report [សារ]")
        return

    bot.send_message(
        ADMIN_ID,
        f"🚨 Report\n"
        f"👤 {m.from_user.first_name} (ID: {m.from_user.id})\n"
        f"💬 {parts[1]}"
    )
    bot.reply_to(m, "✅ បានផ្ញើទៅ Admin ហើយ")

# ---------------- LINK HANDLER ----------------
@bot.message_handler(func=lambda m: True)
def get_link(m):
    url = m.text.strip()

    if not url.startswith("http"):
        bot.reply_to(m, "❌ លីងមិនត្រឹមត្រូវ!")
        return

    user_links[m.chat.id] = {
        "url": url,
        "time": time()
    }

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🎬 MP4 (Video)", callback_data="mp4"),
        InlineKeyboardButton("🎵 MP3 (Audio)", callback_data="mp3"),
        InlineKeyboardButton(
            "📢 Share Bot",
            url="https://t.me/share/url?url=https://t.me/Gerrard_Bot"
        )
    )
    bot.reply_to(m, "👇 សូមជ្រើសរើសប្រភេទឯកសារ៖", reply_markup=markup)

# ---------------- DOWNLOAD & SEND ----------------
@bot.callback_query_handler(func=lambda call: True)
def download_choice(call):
    chat_id = call.message.chat.id
    data = user_links.get(chat_id)

    if not data:
        bot.answer_callback_query(call.id, "❌ សូមផ្ញើលីងម្តងទៀត")
        return

    url = data["url"]
    is_mp3 = call.data == "mp3"

    bot.answer_callback_query(call.id, "⏳ កំពុងចាប់ផ្តើម...")
    msg = bot.send_message(chat_id, "⬇️ កំពុងទាញយកពីប្រព័ន្ធ... សូមរង់ចាំបន្តិច")

    file_prefix = f"file_{chat_id}_{int(time())}"
    outtmpl = f"{file_prefix}.%(ext)s"

    try:
        if is_mp3:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True
            }
        else:
            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": outtmpl,
                "quiet": True
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{file_prefix}.*")
        if not files:
            raise FileNotFoundError("រកមិនឃើញហ្វាយដែលបានទាញយកទេ!")

        file_path = files[0]

        with open(file_path, "rb") as f:
            if is_mp3:
                bot.send_audio(chat_id, f)
            else:
                bot.send_video(chat_id, f)

        os.remove(file_path)
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ មានបញ្ហា: {str(e)[:100]}", chat_id, msg.message_id)
    finally:
        for f in glob.glob(f"{file_prefix}*"):
            try:
                os.remove(f)
            except OSError:
                pass

# ---------------- RUN BOT ----------------
bot.infinity_polling(skip_pending=True)

