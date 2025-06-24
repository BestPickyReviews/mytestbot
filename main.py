import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8189059539:AAFBWa41U-tIOnp1_p85oxHXwOkxTGlsm3U"
MEDIA_API_KEY = "17612vb807jnawfo7brar"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a video or document and I’ll upload it to media.cm!")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.video or update.message.document
    if not file:
        await update.message.reply_text("❗Please send a video or document file.")
        return

    tg_file = await file.get_file()
    file_path = f"temp_{file.file_unique_id}_{file.file_name}"
    await tg_file.download_to_drive(file_path)

    # Step 1: Get upload server
    try:
        server_resp = requests.get(f"https://media.cm/api/upload/server?key={MEDIA_API_KEY}")
        upload_url = server_resp.json().get("result")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to get upload server: {e}")
        return

    # Step 2: Upload to media.cm
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                upload_url,
                files={"file": (file.file_name, f)},
                data={"key": MEDIA_API_KEY, "file_title": file.file_name}
            )
        os.remove(file_path)

        upload_json = response.json()
        if response.status_code == 200 and "files" in upload_json:
            links = [f"https://media.cm/{f['filecode']}" for f in upload_json["files"]]
            await update.message.reply_text("✅ Upload successful:\n" + "\n".join(links))
        else:
            await update.message.reply_text("❌ Upload failed. Invalid response from media.cm.")
    except Exception as e:
        await update.message.reply_text(f"❌ Upload error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, handle_media))
    app.run_polling()

if __name__ == "__main__":
    main()
