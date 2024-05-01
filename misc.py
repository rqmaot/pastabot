import json
import os
import validators
import yt_dlp

# utilities for the bot:
# get_mp3(link) returns filepath for downloaded mp3
# rm(filepath) deletes the file (use after sending get_mp3 output)

def _check_url(url):
    if validators.url(url):
        return True
    if validators.url("http://" + url):
        return True
    return False

def _new_extension(filename, new_extension):
    dot_index = filename.rfind('.')
    if dot_index != -1:
        return filename[:dot_index] + '.' + new_extension
    else:
        return filename + '.' + new_extension

def _ytdlp(link):
    ydl_opts = {
        'format': "139",
        'quiet': True,
        'restrictfilenames': True
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info = ydl.extract_info(link)
    return info['title']

def get_mp3(link):
    if not _check_url(link):
        return None
    original_files = os.listdir(os.getcwd())
    name = _ytdlp(link)
    filename = ""
    for file in os.listdir(os.getcwd()):
        if file not in original_files:
            filename = file
            break
    mp3 = name + ".mp3"
    mp3_escaped = mp3.replace("'", "\\'").replace('/', ' ⁄')
    #os.system(f"yt-dlp -x {link} -o ytdlp > /dev/null")
    os.system(f"ffmpeg -nostdin -i {filename} '{mp3_escaped}' 2> /dev/null")
    os.remove(filename)
    return "./" + mp3.replace('/', ' ⁄')

def rm(file):
    print(f"removing {file}")
    os.remove(file)

def get_sound(sound):
    try:
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
            with open(config["sounds"]) as sounds_file:
                sounds = json.loads(sounds_file.read())
                return sounds["prefix"] + "/" + sounds["sounds"][sound]
    except Exception as e:
        print(e)
        return None
