import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp
from flask import Flask
from threading import Thread

app_flask = Flask('')
@app_flask.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not ("http://" in url or "https://" in url):
        await update.message.reply_text("እባክዎ ትክክለኛ የቪዲዮ ሊንክ ይላኩ (TikTok, Instagram, Pinterest, Telegram)")
        return

    await update.message.reply_text("⏳ ቪዲዮውን በማውረድ ላይ ነው፣ እባክዎ ይጠብቁ...")
    output_template = 'downloaded_video.mp4'
    ydl_opts = {'format': 'best', 'outtmpl': output_template}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(output_template, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        if os.path.exists(output_template):
            os.remove(output_template)
    except Exception as e:
        await update.message.reply_text(f"ይቅርታ፣ ማውረድ አልተቻለም: {str(e)}")
        if os.path.exists(output_template):
            os.remove(output_template)

if __name__ == '__main__':
    keep_alive()
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("ቦቱ በሰርቨር ላይ በመሥራት ላይ ነው...")
    app.run_polling()
