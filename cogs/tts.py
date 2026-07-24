from discord.ext import commands
from gtts import gTTS
import os
import re
import time

def generate(speech, msgid, lang='en', tld='co.uk'):
    try: os.mkdir('tts')
    except: pass
    os.mkdir(f'tts/{msgid}')
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
                return None
    return gen_with_args(True, True)

def clean_msg(msg):
    ignore = ["!", "http", ":", "<"]
    keep_capital = ["AI", "VR", "NHS"]
    def map_word(word):
        if True in map(lambda x: word.startswith(x), ignore): return ''
        if word == word.upper() and word not in keep_capital: return word.lower()
        return word
    return ' '.join(map(map_word, re.split('() ', msg)))

class Tts(commands.Cog):
    def __init__(self, app):
        self.app = app
    async def speak(self, ctx, filename, filedir):
        try:
            vc = await self.app.connect_to_vc(ctx)
            async with self.app.musicq.lock:
                self.app.musicq.add(f'{filedir}/{filename}', dir_to_rm=filedir, vc=vc, track=1)
        except Exception as e:
            await ctx.send(f'tts.speak: {e}')
    def add_tts(self, ctx, user_id, tld, lang):
        if not self.app.config.exists('tts'): self.app.config.add('tts', {})
        if str(user_id) not in self.app.config.get('tts'): 
            self.app.config.get('tts')[str(user_id)] = {}
        self.app.config.get('tts')[str(user_id)][str(ctx.channel.id)] = {
                'tld': tld, 
                'lang': lang
            }
        self.app.config.save()
    def remove_tts(self, ctx, user_id):
        if not self.app.config.exists('tts'): return
        if str(user_id) not in self.app.config.get('tts'): return
        if str(ctx.channel.id) not in self.app.config.get('tts')[str(user_id)]: return
        del self.app.config.get('tts')[str(user_id)][str(ctx.channel.id)]
        self.app.config.save()
    @commands.command(help='Activate TTS. For yourself, use !tts [tld (e.g. us or co.uk)] [lang (e.g. en)]. Default is co.uk en')
    async def tts(self, ctx, user_id=None, tld=None, lang=None):
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        if lang is None and user_id is not None and len(user_id) < 8: lang, tld, user_id = tld, user_id, None
        if user_id is None: user_id = str(ctx.author.id)
        if tld is None: tld = "co.uk"
        if lang is None: lang = 'en'
        if user_id != str(ctx.author.id) and await self.app.auth.verify(ctx, auth.MODERATOR): return
        self.remove_tts(ctx, user_id)
        self.add_tts(ctx, user_id, tld, lang)
    @commands.command(help='Deactivate TTS')
    async def notts(self, ctx, user_id=None):
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        if user_id is None: user_id = str(ctx.author.id)
        if user_id != str(ctx.author.id) and await self.app.auth.verify(ctx, auth.MODERATOR):
            return
        self.remove_tts(ctx, user_id)
    @commands.command(help='Get list of TLDs for TTS')
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
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.app.bot.get_context(msg)
        if not self.app.config.exists('tts'): return
        if str(ctx.author.id) not in self.app.config.get('tts'): return
        if str(ctx.channel.id) not in self.app.config.get('tts')[str(ctx.author.id)]: return
        entry = self.app.config.get('tts')[str(ctx.author.id)][str(ctx.channel.id)]
        if msg.content.startswith("!"): return
        content = clean_msg(msg.content.replace('(', ' ').replace(')', ' ').replace('https', ' https'))
        if content.strip() == '': return
        filename, filedir = generate(content, str(msg.id), entry['lang'], entry['tld'])
        await self.speak(ctx, filename, filedir)

