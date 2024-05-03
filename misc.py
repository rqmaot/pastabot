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

def get_config():
    try:
        with open("config.json") as config_file:
            return json.loads(config_file.read())
    except:
        return None

def get_sounds_json(config):
    try:
        with open(config["sounds"]) as sounds_file:
            return json.loads(sounds_file.read())
    except:
        return None

def get_sound(sound):
    sounds = get_sounds_json(get_config())
    if sounds == None:
        return None
    # i know i should just check if the sound is in sounds['sounds'] and return sound['sounds'][sound]
    # but python is stupid and gave a type error when the key had a space in it and i am not debugging that
    # first check: there is a key for the sound given
    for key in sounds['sounds']:
        if key == sound:
            return sounds["prefix"] + "/" + key
    # second check: there is a key containing/contained in the sound given
    for key in sounds['sounds']:
        if sound in key or key in sound:
            return sounds['prefix'] + '/' + key
    # last check: a sound file contains the sound given
    files = os.listdir(sounds["prefix"])
    for file in files:
        if sound in file:
            return sounds["prefix"] + "/" + file
    return None
