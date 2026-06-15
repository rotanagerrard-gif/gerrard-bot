import telebot, yt_dlp, os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7508538976:AAFDO9hexlJ4Ef5FEF3xDFNgf9HF-rX15_Q")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7097515717"))

bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "👋 សួស្តី! សូមផ្ញើលីងវីដេអូ TikTok ឬ YouTube មក។\n📌 រាយការណ៍បញ្ហា វាយ៖ /report [សារ]")

@bot.message_handler(commands=['update'])
def update_bot(m):
    if m.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(m, "⏳ កំពុង Update...")
    try:
        os.system("pip install --upgrade yt-dlp")
        bot.edit_message_text("✅ Update ជោគជ័យ!", m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ បរាជ័យ៖ {str(e)}", m.chat.id, msg.message_id)

@bot.message_handler(commands=['report'])
def report(m):
    parts = m.text.split(" ", 1)
    if len(parts) < 2:
        bot.reply_to(m, "❌ វាយ៖ /report [សាររបស់បង]")
        return
    bot.send_message(ADMIN_ID, f"🚨 ការរាយការណ៍ពី៖ {m.from_user.first_name} (ID: {m.from_user.id})\n💬 សារ៖ {parts[1]}")
    bot.reply_to(m, "✅ បានផ្ញើទៅកាន់អ្នកគ្រប់គ្រងរួចរាល់។")

@bot.message_handler(func=lambda m: True)
def get_link(m):
    url = m.text
    if not url.startswith("http"):
        bot.reply_to(m, "❌ លីងមិនត្រឹមត្រូវ!")
        return
    user_links[m.chat.id] = url
    markup = InlineKeyboardMarkup(row_width=2)  # ✅ កែត្រូវ row_width
    markup.add(
        InlineKeyboardButton("🎬 វីដេអូ (MP4)", callback_data="mp4"),
        InlineKeyboardButton("🎵 ចម្រៀង (MP3)", callback_data="mp3"),
        InlineKeyboardButton("📢 ចែករំលែក Bot", url="https://t.me/share/url?url=https://t.me/Gerrard_Bot&text=សាកប្រើ%20Bot%20ដោនឡូតវីដេអូនិងចម្រៀងនេះមើលបងៗ%20លឿនណាស់!")
    )
    bot.reply_to(m, "👇 សូមជ្រើសរើស៖", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download_choice(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url: return

    bot.answer_callback_query(call.id, "⏳ កំពុងដំណើរការ...")
    msg = bot.send_message(chat_id, "⏳ កំពុងទាញយក...")
    is_mp3 = (call.data == "mp3")

    try:
        if is_mp3:
            ydl_opts = {
                'format': 'ba/b',
                'outtmpl': f"file_{chat_id}.%(ext)s",  # ✅ កែត្រូវ extension
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            }
        else:
            ydl_opts = {
                'format': 'best[filesize<50M]/best',  # ✅ កំណត់ទំហំ
                'outtmpl': f"file_{chat_id}.%(ext)s",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = "mp3" if is_mp3 else info.get("ext", "mp4")
            file_name = f"file_{chat_id}.{ext}"

        # ✅ ត្រួតពិនិត្យទំហំឯកសារ
        if os.path.exists(file_name) and os.path.getsize(file_name) > MAX_FILE_SIZE:
            bot.edit_message_text("❌ ឯកសារធំពេក! លើស 50MB។", chat_id, msg.message_id)
            os.remove(file_name)
            return

        with open(file_name, "rb") as f:
            if is_mp3:
                bot.send_audio(chat_id, f)
            else:
                bot.send_video(chat_id, f)

        os.remove(file_name)
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:  # ✅ កែត្រូវ except
        print(f"[ERROR] {e}")
        bot.edit_message_text("❌ មិនអាចទាញយកបានទេ។", chat_id, msg.message_id)
        for f in os.listdir('.'):
            if f.startswith(f"file_{chat_id}"):
                os.remove(f)

bot.polling()
