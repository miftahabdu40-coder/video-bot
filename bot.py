import os
import logging
from flask import Flask
from threading import Thread
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# የ /start ትእዛዝ ሲላክ የሚሰጠው ምላሽ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም ሚፍታህ! 🚀 እኔ Miff Video Downloader ቦት ነኝ።\n\n"
        "የ TikTok፣ Instagram ወይም Pinterest ቪዲዮ ሊንክ ላኩልኝ፣ ወዲያውኑ አውርጄ እሰጥዎታለሁ!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not ("http://" in url or "https://" in url):
        await update.message.reply_text("⚠️ እባክዎ ትክክለኛ የቪዲዮ ሊንክ (TikTok, Instagram, Pinterest) ይላኩ")
        return

    status_msg = await update.message.reply_text("⏳ ቪዲዮውን በማውረድ ላይ ነው፣ እባክዎ ትንሽ ይጠብቁ...")
    output_template = 'downloaded_video.mp4'
        ydl_opts = {
        'format': 'best',
        'outtmpl': output_template,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(output_template, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        if os.path.exists(output_template):
            os.remove(output_template)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
    except Exception as e:
        await update.message.reply_text(f"❌ ቪዲዮውን ማውረድ አልተቻለም: {str(e)}")
        if os.path.exists(output_template):
            os.remove(output_template)

if __name__ == '__main__':
    keep_alive()
    TOKEN = os.environ.get("BOT_TOKEN")
    
    # የጊዜ ገደብ (Timeouts) የተስተካከለበት ትክክለኛ ግንኙነት
    application = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).pool_timeout(30).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is active and running 24/7!")
    application.run_polling()
    
