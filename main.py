import logging
import asyncio
import os
import sys
import threading
import subprocess
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen

# --- 1. PYTHON 3.12+ LOOP FIX (Render Error Fix) ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# --- 2. RENDER 24/7 SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- 3. CONFIGURATION ---
API_ID = 38758234
API_HASH = "a3e2c6c938fecb485a83fd57ef38bd74"
BOT_TOKEN = "8541206964:AAFwhvSmpfvM7ntCYifuy2yoAxVfo62EAoE"
AUTH_USERS = [1392259010]

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 4. START COMMAND ---
@bot.on_message(filters.command("start") & filters.user(AUTH_USERS))
async def batch_start(bot, m: Message):
    editable = await m.reply_text(f"👋 **Hey {m.from_user.first_name}**\nSend .txt file or Link")
    
    try:
        input_msg = await bot.listen(m.chat.id)
        links = []
        
        # TXT File handling
        if input_msg.document:
            path = await input_msg.download()
            with open(path, "r") as f:
                for line in f:
                    if "://" in line:
                        links.append(line.strip().split("://", 1))
            os.remove(path)
        # Single Link handling
        elif input_msg.text and "://" in input_msg.text:
            links.append(input_msg.text.strip().split("://", 1))

        if not links:
            return await editable.edit("No valid links found!")

        await editable.edit(f"🔗 Found **{len(links)}** links. Send Start Index (e.g. 1):")
        count = int((await bot.listen(m.chat.id)).text)

        await editable.edit("📝 **Enter Batch Name:**")
        b_name = (await bot.listen(m.chat.id)).text

        await editable.edit("🎬 **Resolution (144, 360, 480, 720):**")
        res_choice = (await bot.listen(m.chat.id)).text

        await editable.edit("🔑 **PW/Token (or 'No'):**")
        token = (await bot.listen(m.chat.id)).text

        await editable.delete()

        import helper 
        for i in range(count - 1, len(links)):
            try:
                url = "https://" + links[i][1]
                name = f"{str(count).zfill(3)}) {links[i][0].strip()[:60]}"
                caption = f"**{name}**\n**Batch:** {b_name}"
                
                # Download via helper.py
                res_file = await helper.download_video(url, name, res_choice, token)
                if res_file:
                    await helper.send_vid(bot, m, caption, res_file, "No", name)
                
                count += 1
                await asyncio.sleep(1) # Flood avoid karne ke liye
            except Exception:
                count += 1
                continue
        
        await bot.send_message(m.chat.id, "🔰 **All Tasks Done!** 🔰")
    except Exception as e:
        await m.reply(f"⚠️ Error: {e}")

# --- 5. RUN BOT ---
async def main():
    await bot.start()
    print("Bot is LIVE! ✅")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
                                                
