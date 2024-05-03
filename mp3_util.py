import json
import os
import validators
import yt_dlp

try:
    os.system("rm -r mp3-*")
except:
    pass

suffix = [0]

def _ytdlp(link):
    options = {
        'format': '139',
        'quiet': True,
        'restrictfilenames': True
    }
    ydl = yt_dlp.YoutubeDL(options)
    info = ydl.extract_info(link)
    return info['title']

def get_mp3(link):
    if not validators.url(link):
        return (None, None)
    mp3_dir = f"mp3-{suffix[0]}"
    suffix[0] += 1
    os.mkdir(mp3_dir)
    os.chdir(mp3_dir)
    title = _ytdlp(link)
    filename = os.listdir('./')[0]
    mp3 = title + '.mp3'
    mp3_escaped = mp3.replace("'", "\\'").replace('/', ' ⁄')
    os.system(f"ffmpeg -nostdin -i {filename} '{mp3_escaped}'")
    os.remove(filename)
    os.chdir('../')
    return (mp3, mp3_dir)

def rmdir(d):
    os.rmdir(d)
