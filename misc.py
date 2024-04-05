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
        'quiet': 'true'
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info = ydl.extract_info(link)
    return info['title']

def get_mp3(link):
    if not _check_url(link):
        return None
    name = _ytdlp(link)
    filename_escaped = name.replace(" ", "\\ ")
    mp3 = name + ".mp3"
    mp3_escaped = mp3.replace(" ", "\\ ")
    #os.system(f"yt-dlp -x {link} -o ytdlp > /dev/null")
    os.system(f"ffmpeg -nostdin -i {filename_escaped}* {mp3_escaped} 2> /dev/null")
    os.system(f"rm {filename_escaped}*m4a")
    return "./" + mp3

def rm(file):
    file = file.replace(" ", "\\ ")
    print(f"removing {file}")
    os.system(f"rm {file}") 

