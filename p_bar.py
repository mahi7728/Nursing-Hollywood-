import time
import math
import os
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta

class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

def hrb(value, digits=2, delim="", postfix=""):
    if value is None: return None
    chosen_unit = "B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1024: # Yahan 1000 ko 1024 kar diya (standard)
            value /= 1024
            chosen_unit = unit
        else: break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix

def hrt(seconds, precision=0):
    pieces = []
    value = timedelta(seconds=seconds)
    if value.days: pieces.append(f"{value.days}d")
    seconds = value.seconds
    if seconds >= 3600:
        hours = int(seconds / 3600)
        pieces.append(f"{hours}h")
        seconds -= hours * 3600
    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60
    if seconds > 0 or not pieces: pieces.append(f"{seconds}s")
    return "".join(pieces) if not precision else "".join(pieces[:precision])

timer = Timer()

async def progress_bar(current, total, reply, start):
    if timer.can_send():
        now = time.time()
        diff = now - start
        if diff < 1: return
        
        perc = f"{current * 100 / total:.1f}%"
        speed = current / diff
        remaining_bytes = total - current
        eta = hrt(remaining_bytes / speed, precision=1) if speed > 0 else "-"
        sp = str(hrb(speed)) + "/s"
        tot = hrb(total)
        cur = hrb(current)
        
        bar_length = 12
        completed = int(current * bar_length / total)
        progress_bar_str = "▓" * completed + "▒" * (bar_length - completed)
        
        #  @M77extract_bot 
        try:
            await reply.edit(f'** ╭──⌯════🆄︎ᴘʟᴏᴀᴅɪɴɢ⬆️⬆️════⌯──╮\n├⚡ {progress_bar_str}|﹝{perc}﹞\n├🚀 Speed » {sp}\n├📟 Processed » {cur}\n├🧲 Size » {tot}\n├⏳ ETA » {eta}\n╰─═══ ✪@M77extract_bot✪ ═════─╯**') 
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception:
            pass
            
