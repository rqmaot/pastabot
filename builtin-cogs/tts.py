from discord.ext import commands
from gtts import gTTS
import os
from piper import PiperVoice
import re
import subprocess
import time
import wave

from app import Auth, command

def file_exists(path):
    try: os.rename(path, path)
    except: return False
    return True

def generate(speech, msgid, lang='en', tld='co.uk', voices=None):
    os.makedirs(f'tts/{msgid}', exist_ok=True)
    def gen_with_args(use_lang, use_tld):
        try:
            if use_lang and use_tld:
                gTTS(speech, lang=lang, tld=tld).save(f"tts/{msgid}/{msgid}.mp3")
            elif use_lang:
                gTTS(speech, lang=lang, tld='co.uk').save(f"tts/{msgid}/{msgid}.mp3")
            elif use_tld:
                gTTS(speech, lang='en', tld=tld).save(f"tts/{msgid}/{msgid}.mp3")
            else:
                gTTS(speech, lang='en', tld='co.uk').save(f"tts/{msgid}/{msgid}.mp3")
            return (f"{msgid}.mp3", f"tts/{msgid}")
        except: 
            if use_lang and use_tld:
                return gen_with_args(True, False)
            elif use_lang: 
                return gen_with_args(False, True)
            elif use_tld: 
                return gen_with_args(False, False)
            else: 
                raise ValueError(f'Cannot generate speech with tld={tld}, lang={lang}')
    if tld != 'piper': return gen_with_args(True, True)
    if voices is None: raise ValueError('No voices provided for piper')
    if lang not in voices:
        os.makedirs('piper', exist_ok=True)
        path = os.path.join('piper', f'{lang}.onnx')
        if not file_exists(path):
            print(f'Downloading piper voice {lang}')
            subprocess.run(['python3', '-m', 'piper.download_voices',
                            '--download_dir', 'piper', lang])
        if not file_exists(path):
            raise ValueError(f'Failed to download piper voice {lang}')
        print(f'Loading piper voice {lang}')
        voice = PiperVoice.load(path)
        voices[lang] = voice
    else: voice = voices[lang]
    try:
        with wave.open(f'tts/{msgid}/{msgid}.wav', 'wb') as wav_file:
            voice.synthesize_wav(speech, wav_file)
        return (f'{msgid}.wav', f'tts/{msgid}')
    except Exception as e:
        print(f'tts.generate: {e}')
        return None

def clean_msg(msg):
    ignore = ["!", "http", ":", "<"]
    keep_capital = ["AI", "VR", "NHS"]
    def map_word(word):
        if True in map(lambda x: word.startswith(x), ignore): return ''
        if word == word.upper() and word not in keep_capital: return word.lower()
        return word
    return ' '.join(map(map_word, re.split('() ', msg)))

class TTS(commands.Cog):
    def __init__(self, app):
        self.app = app
        self.voices = {}
    async def speak(self, ctx, filename, filedir):
        try:
            vc = await self.app.connect_to_vc(ctx)
            async with self.app.musicq.lock:
                self.app.musicq.add(f'{filedir}/{filename}', dir_to_rm=filedir, vc=vc, track=1)
        except Exception as e:
            await ctx.send(f'tts.speak: {e}')
    async def add_tts(self, ctx, user_id, tld, lang):
        async with self.app.config as config:
            config.get_or('tts', {}).get_or(str(user_id), {})[str(ctx.channel.id)] = {'tld': tld, 'lang': lang}
    async def remove_tts(self, ctx, user_id):
        async with self.app.config as config:
            del config['tts'][str(user_id)][str(ctx.channel.id)]
    @command(help='Activate TTS. For yourself, use !tts [tld (e.g. us or co.uk)] [lang (e.g. en)]. Default is co.uk en', auth=Auth.TRUSTED)
    async def tts(self, ctx, user_id=None, tld=None, lang=None):
        if lang is None and user_id is not None and len(user_id) < 8: lang, tld, user_id = tld, user_id, None
        if user_id is None: user_id = str(ctx.author.id)
        if tld is None: tld = "co.uk"
        if lang is None: lang = 'en'
        if user_id != str(ctx.author.id) and await self.app.auth.verify(ctx, auth.MODERATOR): return
        await self.remove_tts(ctx, user_id)
        await self.add_tts(ctx, user_id, tld, lang)
    @command(help='Deactivate TTS')
    async def notts(self, ctx, user_id=None):
        if user_id is None: user_id = str(ctx.author.id)
        if user_id != str(ctx.author.id) and await self.app.auth.verify(ctx, auth.MODERATOR):
            return
        await self.remove_tts(ctx, user_id)
    @command(help='Get list of TLDs for TTS')
    async def vtts(self, ctx):
        await ctx.send("""Available tts accents:
Australia - com.au
United Kingdom - co.uk
United States - us
Canada - ca
India - co.in
Ireland ie
South Africa - co.za
Nigeria - com.ng""")
    @command(help='Show info on using Piper TTS')
    async def piper(self, ctx):
        msg = '''To use a piper voice, use `!tts piper [voice code]`.
        You can get voice codes from https://rhasspy.github.io/piper-samples
        (choose parameters and copy the code, which looks like en_US-amy-medium'''
        await ctx.send(msg)
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.app.bot.get_context(msg)
        if 'tts' not in self.app.config: return
        if str(ctx.author.id) not in self.app.config['tts']: return
        if str(ctx.channel.id) not in self.app.config['tts'][str(ctx.author.id)]: return
        entry = self.app.config['tts'][str(ctx.author.id)][str(ctx.channel.id)].json
        if msg.content.startswith("!"): return
        content = clean_msg(msg.content.replace('(', ' ').replace(')', ' ').replace('https', ' https'))
        if content.strip() == '': return
        try:
            filename, filedir = generate(content, str(msg.id), entry['lang'], entry['tld'], self.voices)
        except Exception as e:
            await ctx.send(f'tts.generate: {e}')
            return
        await self.speak(ctx, filename, filedir)

