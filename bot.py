import json
import discord
from discord.ext import commands
from db import db
import misc

def get_token():
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        return config["token"]

TOKEN = get_token()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def player_res(ctx, player_list):
    if len(player_list) == 0:
        return await ctx.send("No data")
    str_list = []
    cum_len = []
    start = 0
    for i in range(len(player_list)):
        if i > 0 and cum_len[i - 1] >= 1500:
            cur = ""
            for x in range(start, i - 1):
                cur += str_list[x] + "\n"
            try:
                await ctx.send(cur)
            except:
                i1 = player_list[i - 1]
                await ctx.send(f'--------------------------------------\n{i1["NAME"][-1]}   [{i1["ID"]}]')
                buf = ""
                for n in range(len(i1["NAME"])):
                    if len(buf) >= 1500:
                        await ctx.send(buf)
                        buf = ""
                    buf += i1["NAME"][n]
                    if n + 1 < len(i1["NAME"]):
                        buf += ", "
                await ctx.send(buf)
            start = i - 1
            cum_len[i - 1] = len(str_list[i - 1])
        str_list.append(db.player_string(player_list[i]))
        cum_len.append(len(str_list[i]))
        if i > 0:
            cum_len[i] += cum_len[i - 1]
    cur = ""
    to_finish = len(str_list)
    for i in range(start, len(str_list)):
        if cum_len[i] < 1500:
            cur += str_list[i] + "\n"
        else:
            to_finish = i
            break
    await ctx.send(cur)
    for i in range(to_finish, len(str_list)):
        await ctx.send(str_list[i])


@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.command()
async def ping(ctx):
    await ctx.send('pong!')

@bot.command()
async def id(ctx, player_id):
    players = db.query_id(player_id)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@bot.command()
async def name(ctx, name):
    players = db.query_name(name)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@bot.command()
async def list(ctx, *, args):
    liststr = ""
    for arg in args:
        liststr += f"{arg}"
    list_response = db.parse_list(liststr)
    for i in range(len(list_response)):
        (name, uuid, discord_id, query) = list_response[i]
        try:
            user = await bot.fetch_user(int(discord_id))
        except:
            user = {"id": discord_id}
        list_response[i] = (name, uuid, user, query)
    messages = db.list_messages(list_response)
    for msg in messages:
        await ctx.send(msg)

@bot.command()
async def mp3(ctx, link):
    filepath = misc.get_mp3(link)
    if filepath == None:
        await ctx.send("Invalid link")
    await ctx.send(file=discord.File(filepath))
    try:
        await ctx.message.delete()
    except Exception as e:
        print(e)
    misc.rm(filepath)

@bot.command()
async def dm(ctx, user_id, *, args):
    if ctx.author.id != 1003070068206354473:
        await ctx.send("you are not authorized to use this command")
        return
    msg = ""
    for word in args:
        msg += word
    user = await bot.fetch_user(int(user_id))
    channel = user.dm_channel
    if channel == None:
        channel = await bot.create_dm(user)
    await channel.send(msg)

@bot.command()
async def find(ctx, discord_id):
    user = await bot.fetch_user(int(discord_id))
    await ctx.send(str(user))

@bot.command()
async def whoami(ctx):
    await ctx.send(ctx.author.id)

@bot.command()
async def help(ctx):
    msg = "Available commands: !id, !name, !ping, !list, !mp3, !help\n"
    msg += "- `!id ID_HERE` : search a player by their id (you can find it by running list in the raot console)\n"
    msg += "- `!name NAME_HERE` : search a player by their name. case insensitive\n"
    msg += "- `!ping` : responds with \"pong!\", useful for checking if the bot is online\n"
    msg += "- `!list PASTE_LIST_OUTPUT` : paste the output of the list command to query every player in a lobby\n"
    msg += "- `!mp3 LINK_HERE` : get an mp3 from a youtube video\n"
    msg += "- `!help` : display this message\n"
    await ctx.send(msg)

bot.run(TOKEN)
