import os
import logging
import requests
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from io import BytesIO
from flask import Flask
from threading import Thread

# ----------------- 1. FLASK WEB SERVER (សម្រាប់ការពារ Render មិនឱ្យបិទ Bot) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------- 2. TELEGRAM BOT CONFIG -----------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ សូមកំណត់ TELEGRAM_BOT_TOKEN និង GEMINI_API_KEY ក្នុង Environment Variables ជាមុនសិន!")

# កំណត់ Client របស់ Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- COMMAND: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋សួស្ដី! ខ្ញុំជា All-in-One AI Bot របស់អ្នក។\n"
        "✨ អ្នកអាចសួរខ្ញុំរឿងទូទៅ ឬប្រើពាក្យបញ្ជាខាងក្រោម៖\n"
        "🎨 /image [ការពិពណ៌នា] - បង្កើតរូបភាព\n"
        "🎵 /music [ចំណងជើង/ប្រភេទ] - បង្កើតតន្ត្រី\n"
        "🎬 /video [ការពិពណ៌នា] - បង្កើតវីដេអូ"
    )

# --- COMMAND: /image ---
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ចូលការពិពណ៌នាពីរូបភាពដែលអ្នកចង់បង្កើត! ឧទាហរណ៍៖ `/image a cute cat`")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎨 กำลังបង្កើតរូបភាពសម្រាប់ពាក្យ: *{prompt}*...", parse_mode="Markdown")
    
    encoded_prompt = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            photo_file = BytesIO(response.content)
            photo_file.name = "generated_image.jpg"
            await update.message.reply_photo(photo=photo_file, caption=f"🎨 ရូបភាពសម្រាប់៖ {prompt}")
        else:
            await update.message.reply_text("❌ មានបញ្ហាក្នុងការបង្កើតរូបភាព សូមព្យាយាមម្ដងទៀត។")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# --- COMMAND: /music ---
async def music_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ជាក់ចំណងជើង ឬប្រភេទភ្លេង! ឧទាហរណ៍៖ `/music lofi chill beat`")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎵 กำลังបង្កើតតន្ត្រីសម្រាប់ពាក្យ: *{prompt}*...", parse_mode="Markdown")
    
    encoded_prompt = requests.utils.quote(prompt)
    music_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512" # ប្រើ URL ជំនួសតន្ត្រីតាមតម្រូវការ
    await update.message.reply_text(f"🎵 តំណភ្ជាប់តន្ត្រី/សំឡេងរបស់អ្នក៖ {music_url}")

# --- COMMAND: /video ---
async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ជាក់ការពិពណ៌នាវីដេអូ! ឧទាហរណ៍៖ `/video cinematic sunset`")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎬 กำลังបង្កើតវីដេអូសម្រាប់ពាក្យ: *{prompt}*...", parse_mode="Markdown")
    video_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}" # ផ្ដល់ជាตัวอย่าง Link
    await update.message.reply_text(f"🎬 តំណភ្ជាប់វីដេអូរបស់អ្នក៖ {video_url}")

# --- HANDLE TEXT MESSAGES (Gemini AI) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"❌ មានបញ្ហាជាមួយ Gemini AI: {str(e)}")

# ----------------- 3. MAIN FUNCTION -----------------
def main():
    # ចាប់ផ្តើម Flask Server ក្នុង Background Thread
    t = Thread(target=run_flask)
    t.start()

    # ចាប់ផ្តើម Telegram Bot Application
    app_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("image", image_command))
    app_bot.add_handler(CommandHandler("music", music_command))
    app_bot.add_handler(CommandHandler("video", video_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Telegram Bot is polling...")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
