import os

def get_mp3(link):
    os.system(f"yt-dlp -x {link} -o ytdlp > /dev/null")
    os.system("ffmpeg -nostdin -i ytdlp.* yt.mp3 > /dev/null")
    os.system("rm ytdlp.*")
    return "./yt.mp3"

def rm(file):
    os.system(f"rm {file}") 
