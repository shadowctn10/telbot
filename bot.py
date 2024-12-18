import os
import requests
from deep_translator import GoogleTranslator  # کتابخانه ترجمه
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
from pydub import AudioSegment

# --- متغیرهای مهم ---
TOKEN = "7830811506:AAHviqGsjxf1S57-W46F5bu9Rh9kuZIQ-fY"  # توکن ربات تلگرام
GENIUS_API_TOKEN = "1k3ljpOFJhSQs52wnj8MaAnfFqVfLGOzBXUhBakw7aD1SAvQsVqih4RK8ds8CLNx"  # توکن API سایت Genius
DEMO_DURATION_MS = 60000  # مدت زمان دمو (1 دقیقه)

# تنظیم مسیر FFmpeg و ffprobe
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

AudioSegment.converter = ffmpeg.get_ffmpeg_exe()
AudioSegment.ffprobe = ffmpeg.get_ffmpeg_exe()

# --- تابع برای دریافت لیریک ---
def get_lyrics(song_name: str) -> str:
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = "https://api.genius.com/search"
    params = {"q": song_name}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        hits = response.json()["response"]["hits"]
        if hits:
            song_url = hits[0]["result"]["url"]
            return f"📃 متن آهنگ را می‌توانید در لینک زیر مشاهده کنید:\n{song_url}"
        else:
            return "متأسفم! متن آهنگ پیدا نشد. 😔"
    else:
        return "خطا در ارتباط با سرور لیریک!"

# --- تابع ترجمه متن با GoogleTranslator ---
def translate_with_detect(text: str) -> str:
    try:
        translated = GoogleTranslator(source="auto", target="fa").translate(text)  # ترجمه به فارسی
        return f"🌐 ترجمه فارسی:\n{translated}"
    except Exception as e:
        return f"خطا در ترجمه متن: {str(e)}"

# --- هندلر برای دکمه Translate ---
async def translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # استخراج نام آهنگ از callback_data
    song_name = query.data.split(":")[1]
    lyrics = get_lyrics(song_name)

    # ترجمه متن
    translated_lyrics = translate_with_detect(lyrics)

    # ارسال ترجمه به پیوی کاربر
    user_id = query.from_user.id
    await context.bot.send_message(chat_id=user_id, text=translated_lyrics)
    await query.message.reply_text("🌐 ترجمه متن آهنگ به پیوی شما ارسال شد!")

# --- سایر توابع (مانند پردازش دمو و دکمه Lyrics) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! آهنگ خود را ارسال کنید تا دمو و متن لیریک آن را دریافت کنید. 🎵")

# --- تابع اصلی برای اجرای ربات ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(translate_button, pattern="^translate:"))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
