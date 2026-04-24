import os
import re
import datetime
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('session', api_id, api_hash)

def extract_links(text):
    return re.findall(r'https://t\.me/\S+', text)

async def analyze(link):
    match = re.search(r't.me/([^/]+)/(\d+)', link)
    if not match:
        return "❌ رابط غير صحيح"

    username = match.group(1)
    msg_id = int(match.group(2))

    try:
        entity = await client.get_entity(username)
        msg = await client.get_messages(entity, ids=msg_id)
        last = await client.get_messages(entity, limit=1)

        now = datetime.datetime.utcnow()
        last_date = last[0].date.replace(tzinfo=None) if last else None

        if last_date:
            delta = now - last_date
            if delta.days < 2:
                state = "🟢 نشطة"
            elif delta.days < 7:
                state = "🟡 متوسطة"
            else:
                state = "🔴 مهجورة"
        else:
            state = "غير معروف"

        return f"""
📊 تقرير
🔗 @{username}
📌 الرسالة: {"موجودة" if msg else "محذوفة"}
📡 الحالة: {state}
🕒 آخر نشاط: {last_date}
"""

    except:
        return f"🔒 @{username} غير متاح"

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    links = extract_links(text)

    if not links:
        await update.message.reply_text("أرسل رابط")
        return

    results = []
    for link in links:
        results.append(await analyze(link))

    await update.message.reply_text("\n".join(results))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل /check + الرابط")

async def main():
    await client.start()

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    await app.run_polling()

import asyncio
asyncio.run(main())
