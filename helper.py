import logging
import subprocess
import datetime
import asyncio
import os
import requests
import json
import time
from p_bar import progress_bar
import aiohttp
import tgcrypto
import aiofiles
from pyrogram.types import Message
from pyrogram import Client, filters

# --- THUMBNAIL GENERATOR ---
async def generate_thumbnail(filename, width=1280, height=720, time_pos="0.0"):
    try:
        thumb_name = f"{filename}.jpg"
        if os.path.exists(thumb_name): os.remove(thumb_name)
        subprocess.run([
            "ffmpeg", "-ss", time_pos, "-i", filename, "-vframes", "1", 
            "-s", f"{width}x{height}", thumb_name
        ], check=True, capture_output=True)
        return thumb_name
    except: return None

# --- DURATION GETTER ---
def get_video_duration(filename):
    try:
        command = ['ffprobe', '-v', 'error', '-show_format', '-print_format', 'json', filename]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = json.loads(result.stdout)
        return int(float(output['format']['duration']))
    except: return 0

# --- VIDEO DOWNLOADER (4 Arguments Fixed) ---
async def download_video(url, name, res_choice, token="No"):
    output_file = f"{name}.mp4"
    if os.path.exists(output_file): os.remove(output_file)

    # yt-dlp command
    command = [
        "yt-dlp",
        "-k", "--allow-unplayable-formats", "--geo-bypass",
        "-f", f"bv*[height<={res_choice}][ext=mp4]+ba[ext=m4a]/b[height<={res_choice}][ext=mp4]/bv*+ba/b",
        "--output", output_file,
        url
    ]
    
    # Agar PW/Token hai toh header add karega
    if token != "No":
        command.extend(["--add-header", f"Authorization:{token}"])

    try:
        subprocess.run(command, check=True)
        return output_file if os.path.exists(output_file) else None
    except Exception as e:
        print(f"Download Failed: {e}")
        return None

# --- VIDEO SENDER ---
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name):
    reply = await m.reply_text(f"⚡ **UPLOADING:** `{name}`")
    
    gen_thumb = await generate_thumbnail(filename)
    thumbnail = thumb if thumb and thumb != "No" else gen_thumb
    duration = get_video_duration(filename)
    start_time = time.time()

    try:        
        await m.reply_video(
            filename, caption=cc, supports_streaming=True, 
            height=720, width=1280, thumb=thumbnail, 
            duration=duration, progress=progress_bar, 
            progress_args=(reply, start_time)
        )
    except Exception as e:
        print(f"Upload Error: {e}")

    # CLEANUP
    if os.path.exists(filename): os.remove(filename)
    if gen_thumb and os.path.exists(gen_thumb): os.remove(gen_thumb)
    await reply.delete()
  
