import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8189059539:AAFBWa41U-tIOnp1_p85oxHXwOkxTGlsm3U"
MEDIA_API_KEY = "17612vb807jnawfo7brar"

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    if not message.startswith("http"):
        await update.message.reply_text("❗ Please send a **direct downloadable video link** (like .mp4, .mkv, etc.)")
        return

    await update.message.reply_text("⏳ Uploading to media.cm... Please wait...")

    media_url = message
    api_url = f"https://media.cm/api/upload/url?key={MEDIA_API_KEY}&url={media_url}"

    try:
        response = requests.get(api_url)
        data = response.json()

        if data.get("status") == 200:
            filecode = data["result"]["filecode"]
            media_link = f"https://media.cm/{filecode}"
            await update.message.reply_text(f"✅ Upload successful:\n{media_link}")
        else:
            await update.message.reply_text(f"❌ Upload failed:\n{data.get('msg')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    app.run_polling()

if __name__ == "__main__":
    main()
