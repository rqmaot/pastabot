import json
import os
import validators
import yt_dlp
import ffmpeg

try:
    os.system("rm -r mp3-*")
except:
    pass

suffix = 0

def _ytdlp(link):
    options = {
        'quiet': True,
        'restrictfilenames': True,
        'noplaylist': True,
        'username': 'oauth2',
        'password': ''
    }
    ydl = yt_dlp.YoutubeDL(options)
    info = ydl.extract_info(link)
    return info['title']

def _get_mp3(link):
    if not validators.url(link):
        return (None, None)
    global suffix
    mp3_dir = f"mp3-{suffix}"
    suffix += 1
    os.mkdir(mp3_dir)
    os.chdir(mp3_dir)
    title = _ytdlp(link)
    filename = os.listdir('./')[0]
    mp3 = title + '.mp3'
    mp3_escaped = mp3.replace('/', ' ⁄').replace('\\', '')
    # os.system(f"ffmpeg -nostdin -i {filename} \"{mp3_escaped}\"")
    ffmpeg.input(filename).output(mp3_escaped).run()
    os.remove(filename)
    os.chdir('../')
    return (mp3, mp3_dir)

def get_mp3(link):
    cwd = os.path.abspath('./')
    try:
        res = _get_mp3(link)
        return res
    except Exception as e:
        os.chdir(cwd)
        raise e

def rmdir(d):
    os.rmdir(d)
