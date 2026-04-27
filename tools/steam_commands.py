import discord
from discord.ext import commands, tasks
import requests
import datetime

auth = None
CONFIG = None
bot = None

class GameInfo:
    def __init__(self, name, initial, final):
        self.name = name
        self.initial = initial
        self.final = final
        self.on_sale = final < initial
        self.percent = round(100 * (initial - final) / initial)
    def __str__(self):
        if self.on_sale:
            return f"{self.name} is {self.percent}% off (${self.initial/100} -> ${self.final/100})"
        return f"{self.name} is not on sale (${self.initial/100})"
    def __repr__(self):
        return f"GameInfo {{name={self.name}, initial={self.initial}, final={self.final}}}"

def get_game_info(app_id):
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": app_id, "cc": "us"}
    res = requests.get(url, params=params)
    if res.status_code != 200: raise ValueError(f"Could not fetch game {app_id}")
    data = res.json()[str(app_id)]["data"]
    try:
        return GameInfo(
                data["name"], 
                data["price_overview"]["initial"], 
                data["price_overview"]["final"]
        )
    except Exception as e: raise ValueError(f"Couldn't get data for {app_id}: {e}")

@commands.command()
async def steam(ctx, app_id):
    if not CONFIG.exists("steam"): CONFIG.set("steam", {})
    user_id = str(ctx.author.id)
    if user_id not in CONFIG.get("steam"): CONFIG.get("steam")[user_id] = {}
    if app_id in CONFIG.get("steam")[user_id]:
        name = CONFIG.get("steam")[user_id][app_id]["name"]
        await ctx.send(f"Will no longer watch {name} for you")
        del CONFIG.get("steam")[user_id][app_id]
        CONFIG.save()
        return
    try:
        info = get_game_info(int(app_id))
        CONFIG.get("steam")[user_id][app_id] = {"name": info.name, 
                                                "prev": info.final, 
                                                "channel": str(ctx.channel.id)}
        CONFIG.save()
        await ctx.send(f"Will watch {info.name} for you. Currently, {info}")
    except Exception as e: await ctx.send(e)

@tasks.loop(hours=8)
async def check_sales():
    messages = {}
    if not CONFIG.exists("steam"): return
    for user_id in CONFIG.get("steam"):
        messages[user_id] = {'sale': '', 'nosale': []}
        sales = {}
        for app_id in CONFIG.get("steam")[user_id]:
            try:
                info = get_game_info(int(app_id))
                if info.final < CONFIG.get("steam")[user_id][app_id]["prev"]:
                    notif_channel = int(CONFIG.get("steam")[user_id][app_id]["channel"])
                    if notif_channel in sales: sales[notif_channel].append(info)
                    else: sales[notif_channel] = [info]
                else: messages[user_id]['nosale'].append(info)
                CONFIG.get("steam")[user_id][app_id]["time"] = str(datetime.datetime.now())
                CONFIG.get("steam")[user_id][app_id]["prev"] = info.final
                CONFIG.save()
            except: pass
        messages[user_id]['nosale'] = '\n'.join(map(str, messages[user_id]['nosale']))
        if len(sales) == 0: continue
        async def ping_user(channel_id):
            msg = "\n".join(map(str, sales[channel_id]))
            channel = await bot.fetch_channel(channel_id)
            if channel is None or channel.type == discord.ChannelType.private:
                return msg
            await channel.send(f"<@{user_id}>\n{msg}")
            return msg
        user = await bot.fetch_user(int(user_id))
        channel = user.dm_channel
        if channel is None: channel = await bot.create_dm(user)
        msg = "\n".join(map(ping_user, sales))
        await channel.send(msg)
        messages[user_id]['sale'] = msg
        # await channel.send("\n".join(map(str, sales)))
    return messages

@commands.command()
async def steamdebug(ctx):
    if await auth.verify(ctx, auth.MODERATOR): return
    messages = await check_sales()
    for user_id in messages:
        await ctx.send(f"To <@{user_id}>:\nSales:\n{messages[user_id]['sale']}\nNo sales:\n{messages[user_id]['nosale']}")

def init(the_bot):
    global bot 
    bot = the_bot
    check_sales.start()

commands = [steam, steamdebug]
helps = ["!steam <app_id> : add/remove a game to be notified when it's on sale"]
