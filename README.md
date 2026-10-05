# Pastabot

Pastabot is an easily extensible Discord bot made with discord.py. 
The basic framework provides an `Auth` class and a connected decorator 
`@command`, which is the same as discord.py's `@command` decorator, with an 
added `auth` argument enabling commands to require a certain auth level without
requiring a manual check inside the command function body.

Cogs are loaded onto the bot dynamically from the cog directories provided to
the `App` constructor. They are provided the app root in their path, so loaded
cogs can import from `app` or `tools` as needed. To add a cog, you simply write
a subclass of `discord.commands.Cog` which takes a single `App` argument in its
constructor. The app will load all `.py` files which don't start with `_` from
all the cog directories it is constructed with, and for each 
`discord.commands.Cog` class (say `MyCog`), it will add an instance of that cog
to the bot with `bot.add_cog(MyCog(app))`. You therefore don't need to change
any code to add a cog; simply write one in the `custom-cogs` directory and it
will be loaded automatically.

Pastabot additionally provides the `Config` class, a utility for managing JSON
files. The bot loads `config.json`, and the corresponding `Config` is available
to any cog through `self.app.config`. You can think of a `Config` as a
read-only dictionary. To write to the config, you can obtain a writable version
within a `with async` block. The config is saved to disk when the block exits.
Be aware that any changes you make to the config using a text editor while the
bot is running are likely to be overwritten when the bot saves its own changes.
If you wish to manually edit the config, you should first ensure that the bot is
not running.

A simple `config.json` might look like this:
```
{
    "token": "YOUR_DISCORD_BOT_TOKEN",
    "auth": {
        "admin": {
            "some_admin_discord_id": "discord_username"
        }
    }
    "sounds": {
        "prefix": "/path/to/sounds" 
    }
}
```

Strictly speaking, only the `"token"` field is required to run the bot. However,
if the `"auth"` field is not provided, everyone will have no auth by default,
which only allows basic commands. For the most part, you should manage the auth 
config using the bot's `!auth` command. However, it is impossible to add admins 
with this command, so any admin users will need to be added to the config 
manually. Additionally, the `!auth` command requires that the caller have an
auth level higher than both the user whose auth they are trying to modify and
the level they are trying to set their auth to, so even if you don't want any
admin users, you will need to manually add at least one user at the highest
auth level you do want in order to be able to use the `!auth` command to
authorize users at lower levels. As noted before, any manual editing of the
config should be done while the bot is not running.

Note that the auth levels used by Pastabot are specific to Pastabot; the bot
does not use or reference a user's Discord server auth level at any time. This
means that a user's Pastabot auth level is cross-server; if they have a certain
auth level in one server, they have that same level in every server. This can
effectively give a user who is not a server moderator some of the powers of a
server moderator if they are a Pastabot moderator in a server in which Pastabot
has moderation privileges.

The bot also provides a multi-track sound queue with `tools/musicq.py` and
`tools/mixer.py`. Cogs can add sounds to a track using `self.app.musicq.add`,
and the bot will play the sound in VC. Multiple tracks can be played
simultaneously, which is utilized by the built-in cogs `sounds.py` and `tts.py`
to allow users to use TTS while the bot is playing other sounds.

Several cogs are provided in `builtin-cogs`:
    - `basics.py` provides an `on_ready` notifier and the commands `ping`,
      `ip`, `echo`, `dm`, `find`, `whoami`, `throw`, and `console`.  
    - `cipher.py` provides the commands `encrypt` and `decrypt`.  
    - `moderation.py` provides the commands `auth`, `delete`, `reset`, `mute`,
      and `unmute`. After the `mute` command is invoked on a user, the bot will
      start deleting any messages they send for 10 minutes. This is obviously
      inferior to Discord's built-in muting functionality, and it is mostly
      intended as a joke, since a user is still able to type and send a message
      only to see it deleted immediately.
    - `rng.py` provides the `rng` and `choose` commands.
    - `shy.py` provides the `shy`, `notshy`, `allow`, and `disallow` commands.
      When a user is registered as shy, if they are unmuted in VC then everyone
      else in VC will be deafened, except those that user has registered as
      being allowed to hear them. Since this has obvious potential for abuse,
      users must have the `trusted` auth level in order to register as shy.
    - `sounds.py` provides the commands `join`, `leave`, `sound`, `stop`,
      `clear`, and `sounds`. It adds sounds from the directory specified by
      `config["sounds"]["prefix"]` to the bot's sound queue.
    - `steam.py` provides the commands `steam` and `steamdebug`. Every 4 hours,
      the bot will check Steam to see if any games are on sale that a user has
      asked the bot to watch for them. If there are new sales, the bot will DM
      the user and also ping them in the channel where they invoked the `steam`
      command.
    - `tts.py` provides the commands `tts`, `notts`, `checktts`, `vtts`, 
      and `piper`. Users can register to have the bot say their messages using
      either the Google Translate API or a Piper model run locally by the bot.
      Note that the latter is typically much slower and uses more memory. The
      bot also only keeps up to five Piper voices loaded at a time.
    - `watchlist.py` provides the commands `watch` and `watched` for managing
      a watchlist. The watchlist is global to the bot.

The `App` class also provides some utility functions which cogs may use:
    - `connect_to_vc` connects the bot to the voice channel it is called from.
    - `get_ip` returns the bot's public-facing IP. Note this requires that the
      bot can call the `curl` command. This also allows your IP to be exposed
      with the `!ip` command if you are running the bot from home. If you
      do not want the bot's IP to be exposed, you can instantiate the app
      with `App(*cog_dirs, enable_ip=False)` and this function will not
      return your IP.
    - `send_dm` sends a DM from the bot.

The built-in cogs provide usage examples for registering commands and using the
tools provided by the app, including the above functions, auth, the config, and
the sound queue.
