import os
import logging
import requests
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from io import BytesIO

# ទាញយក Token និង Key មកពី Environment Variables ដោយសុវត្ថិភាព
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ពិនិត្យមើលក្រែងលោភ្លេចដាក់
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ សូមកំណត់ TELEGRAM_BOT_TOKEN និង GEMINI_API_KEY ក្នុង Environment Variables ជាមុនសិន!")

# កំណត់ Client របស់ Gemini
client = genai.Client(api_key=GEMINI_API_KEY)