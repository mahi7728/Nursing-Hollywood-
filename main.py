import logging
import subprocess
import datetime
import asyncio
import os
import requests
import time
from p_bar import progress_bar
import aiohttp
import tgcrypto
import aiofiles
from pyrogram.types import Message
from pyrogram import Client, filters
from pyromod import listen
from flask import Flask
import threading
import sys
import re
import json

# --- 1. RENDER 24/7 FIX ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# --- 2. CREDENTIALS ---
auth_users = [1392259010]
sudo_users = [1392259010]

bot = Client(
    "bot",
    api_id=38758234,
    api_hash="a3e2c6c938fecb485a83fd57ef38bd74",
    bot_token="8541206964:AAFwhvSmpfvM7ntCYifuy2yoAxVfo62EAoE"
)

# --- 3. COMMANDS ---

@bot.on_message(filters.command(["stop"]))
async def cancel_command(bot: Client, m: Message):
    user_id = m.from_user.id
    if user_id not in auth_users and user_id not in sudo_users:
        return
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    user_id = m.from_user.id
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply(f"**Aap Authorized User nahi hain.**", quote=True)
        return
        
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file or Single Link**")
    
    try:
        input: Message = await bot.listen(editable.chat.id)
        links = []
        file_name = "batch"

        if input.document:
            x = await input.download()
            await input.delete(True)
            file_name, _ = os.path.splitext(os.path.basename(x))
            with open(x, "r") as f:
                content = f.read().split("\n")
            for i in content:
                if "://" in i:
                    links.append(i.split("://", 1))
            os.remove(x)
        elif "://" in input.text:
            links.append(input.text.split("://", 1))
            await input.delete(True)
        else:
            await editable.edit("Invalid Input! Send a file or link.")
            return

        await editable.edit(f"Total links found: **{len(links)}**\nSend start index (e.g. 1)")
        input0: Message = await bot.listen(editable.chat.id)
        count = int(input0.text)
        await input0.delete(True)

        await editable.edit("**Enter Batch Name (or 'd')**")
        input1: Message = await bot.listen(editable.chat.id)
        b_name = file_name if input1.text == 'd' else input1.text
        await input1.delete(True)

        await editable.edit("**Resolution? (144, 240, 360, 480, 720, 1080)**")
        input2: Message = await bot.listen(editable.chat.id)
        res_choice = input2.text
        await input2.delete(True)

        await editable.edit("**Enter Credit Name (or 'de')**")
        input3: Message = await bot.listen(editable.chat.id)
        CR = f"[{m.from_user.first_name}]" if input3.text == 'de' else input3.text
        await input3.delete(True)

        await editable.edit("**PW Token or 'No'**")
        input4: Message = await bot.listen(editable.chat.id)
        working_token = input4.text
        await input4.delete(True)

        await editable.edit("**Thumb URL or 'No'**")
        input6: Message = await bot.listen(editable.chat.id)
        thumb_url = input6.text
        await input6.delete(True)
        await editable.delete()

        thumb = "thumb.jpg" if thumb_url.startswith("http") else "No"
        if thumb == "thumb.jpg":
            subprocess.run(["wget", thumb_url, "-O", "thumb.jpg"])

        import helper
        for i in range(count - 1, len(links)):
            url = "https://" + links[i][1]
            name1 = links[i][0].strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            cc = f'**{str(count).zfill(3)}.** {name1}\n**Batch:** {b_name}\n**By:** {CR}'

            try:
                if "drive" in url:
                    ka = await helper.download(url, name)
                    await bot.send_document(m.chat.id, ka, caption=cc)
                    os.remove(ka)
                else:
                    res_file = await helper.download_video(url, name, res_choice)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name)
                count += 1
            except Exception as e:
                await m.reply_text(f"**Error in {name}:** {e}")
                count += 1

        await m.reply_text("🔰 **All Tasks Done!** 🔰")
    except Exception as e:
        await m.reply_text(f"Error: {e}")

bot.run()
