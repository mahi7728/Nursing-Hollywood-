from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait
from pyromod import listen
from p_bar import progress_bar
from subprocess import getstatusoutput
from aiohttp import ClientSession
import helper
import time
import asyncio
import threading
from flask import Flask
import sys
import re
import os

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
auth_users = [5842823617]
sudo_users = [5842823617]

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
        await m.reply(f"**You Are Not Subscribed**", quote=True)
        return
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    user_id = m.from_user.id
    if user_id not in auth_users and user_id not in sudo_users:
        await m.reply(f"**You Are Not Subscribed To This Bot\nContact - @Mahagoraxyz**", quote=True)
        return
        
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")
    input: Message = await bot.listen(editable.chat.id)
    
    if input.document:
        x = await input.download()
        await input.delete(True)
        file_name, ext = os.path.splitext(os.path.basename(x))
        credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
        try:
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            links = []
            for i in content:
                links.append(i.split("://", 1))
            os.remove(x)
        except:
            await m.reply_text("Invalid file input.🥲")
            os.remove(x)
            return
    else:
        content = input.text
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
   
    await editable.edit(f"Total links found: **{len(links)}**\nSend start index (e.g. 1)")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Enter Batch Name (or 'd' for file name)**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    b_name = file_name if raw_text0 == 'd' else raw_text0

    await editable.edit("**Enter resolution (144, 240, 360, 480, 720, 1080)**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    res_map = {"144":"256x144","240":"426x240","360":"640x360","480":"854x480","720":"1280x720","1080":"1920x1080"}
    res = res_map.get(raw_text2, "UN")
    
    await editable.edit("**Enter Name (or 'de' for default)**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    CR = credit if raw_text3 == 'de' else raw_text3

    await editable.edit("**Enter PW Token or 'No'**")
    input4: Message = await bot.listen(editable.chat.id)
    working_token = input4.text
    await input4.delete(True)

    await editable.edit("**Send Thumb URL or 'No'**")
    input6: Message = await bot.listen(editable.chat.id)
    thumb = input6.text
    await input6.delete(True)
    await editable.delete()

    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    count = int(raw_text)
    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("://www.youtube-nocookie.com", "youtu.be").replace("/view?usp=sharing","")
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)
            elif 'classplusapp' in url or "testbook.com" in url:
                url, contentId = url.split('&contentHashIdl=')
                params = {'contentId': contentId, 'offlineDownload': "false"}
                headers = {'x-access-token': f'{working_token}', 'user-agent': 'Mobile-Android'}
                res_json = requests.get("https://api.classplusapp.com", params=params, headers=headers).json()
                url = res_json['drmUrls']['manifestUrl'] if "drm" in url else res_json["url"]
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-907e62cf4891.herokuapp.com{url}?token={working_token}"

            name1 = links[i][0].strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            cc = f'**{str(count).zfill(3)}.** {name1}\n**Batch:** {b_name}\n**By:** {CR}'

            try:
                if "drive" in url:
                    ka = await helper.download(url, name)
                    await bot.send_document(m.chat.id, ka, caption=cc)
                    os.remove(ka)
                elif ".pdf" in url:
                    os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                    await bot.send_document(m.chat.id, f'{name}.pdf', caption=cc)
                    os.remove(f'{name}.pdf')
                else:
                    prog = await m.reply_text(f"**Downloading:** `{name}`")
                    res_file = await helper.download_video(url, name, raw_text2)
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, res_file, thumb, name)
                count += 1
            except Exception as e:
                await m.reply_text(f"**Failed:** `{name}`\nError: {e}")
                count += 1
    except Exception as e:
        await m.reply_text(str(e))
    await m.reply_text("🔰Done Boss🔰")

bot.run()                    
