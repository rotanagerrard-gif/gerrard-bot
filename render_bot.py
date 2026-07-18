import os
import glob
from time import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7508538976:AAFvcqzDt1Cu_P-Sm92xLv8DBhJzqAgnkv4")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7097515717"))

bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "👋 សួស្តី!\n"
                    "📩 ផ្ញើលីង YouTube ឬ TikTok មកទីនេះដើម្បីទាញយក\n"
                    "📌 /report [សារ] ដើម្បីរាយការណ៍")

# ================= UPDATE =================
@bot.message_handler(commands=['update'])
def update_bot(m):
    if m.from_user.id != ADMIN_ID:
        return
    msg = bot.reply_to(m, "⏳ កំពុង Update yt-dlp...")
    try:
        os.system("pip install --upgrade yt-dlp")
        bot.edit_message_text("✅ Update ជោគជ័យ!", m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ បរាជ័យ: {e}", m.chat.id, msg.message_id)

# ================= REPORT =================
@bot.message_handler(commands=['report'])
def report(m):
    parts = m.text.split(" ", 1)
    if len(parts) < 2:
        bot.reply_to(m, "❌ ប្រើ៖ /report [សារ]")
        return
    bot.send_message(ADMIN_ID, f"🚨 Report from {m.from_user.first_name} (ID: {m.from_user.id})\n💬 {parts[1]}")
    bot.reply_to(m, "✅ បានផ្ញើទៅ Admin ហើយ")

# ================= LINK HANDLER =================
@bot.message_handler(func=lambda m: True)
def get_link(m):
    url = m.text.strip()
    if not url.startswith("http"):
        bot.reply_to(m, "❌ លីងមិនត្រឹមត្រូវ!")
        return

    user_links[m.chat.id] = {"url": url, "time": time()}

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎬 MP4 (Video)", callback_data="mp4"),
        InlineKeyboardButton("🎵 MP3 (Audio)", callback_data="mp3"),
        InlineKeyboardButton("📢 Share Bot", url="https://t.me/share/url?url=https://t.me/Gerrard_Bot")
    )
    bot.reply_to(m, "👇 សូមជ្រើសរើសប្រភេទ៖", reply_markup=markup)

# ================= DOWNLOAD =================
@bot.callback_query_handler(func=lambda call: True)
def download_choice(call):
    chat_id = call.message.chat.id
    data = user_links.get(chat_id)
    if not data:
        bot.answer_callback_query(call.id, "❌ ផ្ញើលីងម្តងទៀត")
        return

    url = data["url"]
    is_mp3 = call.data == "mp3"

    bot.answer_callback_query(call.id, "⏳ កំពុងទាញយក...")
    msg = bot.send_message(chat_id, "⬇️ កំពុងទាញយក... សូមរង់ចាំ")

    file_prefix = f"file_{chat_id}_{int(time())}"

    try:
        if is_mp3:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{file_prefix}.%(ext)s",
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
                "outtmpl": f"{file_prefix}.%(ext)s",
                "quiet": True
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{file_prefix}.*")
        if not files:
            raise Exception("រកមិនឃើញហ្វាយល!")

        file_path = files[0]

        with open(file_path, "rb") as f:
            if is_mp3:
                bot.send_audio(chat_id, f)
            else:
                bot.send_video(chat_id, f)

        os.remove(file_path)
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ មានបញ្ហា: {str(e)[:150]}", chat_id, msg.message_id)
    finally:
        for f in glob.glob(f"{file_prefix}*"):
            try:
                os.remove(f)
            except:
                pass

# ================= RUN =================
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling(skip_pending=True)
