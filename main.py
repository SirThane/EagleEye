from discord.ext import commands
from asyncio import sleep
import discord
import sys
import shutil
import redis
import json


try:
    with open('redis.json', 'r') as auth_info:
        db_info = json.load(auth_info)['db']
        db = redis.StrictRedis(**db_info)
except:
    db = None
    print("redis.json not found in cwd.")
    sys.exit()


bot = commands.Bot(command_prefix=")(90f3lkFDlEWo23nmROl24=R{;'afg4gf-", self_bot=True)
bot.w = lambda: shutil.get_terminal_size((80, 25)).columns

@bot.listen()
async def timer_update(seconds):
    return seconds


async def init_timed_events(bot):
    await bot.wait_until_ready()
    bot.secs = 0

    secs = 0
    while True:
        bot.dispatch("timer_update", secs)
        await timer_update(secs)
        secs += 1
        bot.secs = secs
        await sleep(1)


class Listeners:
    def __init__(self, bot):
        self.bot = bot
        self.print_splash()

    # Utility functions

    @property
    def banner(self):
        if self.w >= 74:
            return """
8888888888                   888               8888888888                 
888                          888               888                        
888                          888               888                        
8888888     8888b.   .d88b.  888  .d88b.       8888888   888  888  .d88b. 
888            "88b d88P"88b 888 d8P  Y8b      888       888  888 d8P  Y8b
888        .d888888 888  888 888 88888888      888       888  888 88888888
888        888  888 Y88b 888 888 Y8b.          888       Y88b 888 Y8b.     
8888888888 "Y888888  "Y88888 888  "Y8888       8888888888 "Y88888  "Y8888  
                         888                                  888         
                    Y8b d88P                             Y8b d88P         
                     "Y88P"                               "Y88P"          
"""
        elif self.w >= 49:
            return """
8""""                           8""""             
8     eeeee eeeee e     eeee    8     e    e eeee 
8eeee 8   8 8   8 8     8       8eeee 8    8 8    
88    8eee8 8e    8e    8eee    88    8eeee8 8eee 
88    88  8 88 "8 88    88      88      88   88   
88eee 88  8 88ee8 88eee 88ee    88eee   88   88ee
"""
        elif self.w >= 26:
            return """
.___      .     .___      
[__  _. _ | _   [__   . _ 
[___(_](_]|(/,  [___\_|(/,
       ._|          ._|   
"""

    @property
    def w(self):
        return self.bot.w()

    def print_splash(self):
        print(self.banner)
        if self.bot.owner:
            owner = f'| Owner:     {bot.owner}\n'
        else:
            owner = ""
        print(f'#-------------------------------#\n'
              f'| Successfully logged in.\n'
              f'#-------------------------------#\n'
              f'| Username:  {bot.user.name}\n'
              f'| User ID:   {bot.user.id}\n'
              f'{owner}'
              f'# ------------------------------#\n')

    def check_update(self):
        w = self.w
        print(f"{self.header('UPDATE', '+')}\nUpdating watch/ignore lists from database. . .\n{'+' * w}")
        self.watched_guilds = [int(g) for g in list(db.smembers("eagleeye:watched_guilds"))]
        print(f"  Watched guilds list updated: {', '.join([str(g) for g in self.watched_guilds])}")
        self.ignored_channels = [int(c) for c in list(db.smembers("eagleeye:ignored_channels"))]
        print(f"Ignored channels list updated: {', '.join([str(c) for c in self.ignored_channels])}")
        self.ignored_members = [int(c) for c in list(db.smembers("eagleeye:ignored_members"))]
        print(f"   Ignored users list updated: {', '.join([str(c) for c in self.ignored_members])}")
        print(f"{'+' * w}\n")

    async def on_timer_update(self, s):
        if s % 300 == 0:
            self.check_update()

    def role_change(self, b, a):
        for r in b.roles:
            if r not in a.roles:
                return "REMOVED", r.name
        for r in a.roles:
            if r not in b.roles:
                return "ADDED", r.name

    def handle_mentions(self, message):
        content, members, roles, channels = message.content, [], [], []

        for m in message.mentions:
            content = content.replace(f"<@{m.id}>", f"@{m.nick if m.nick else m.name}")
            content = content.replace(f"<@!{m.id}>", f"@{m.nick if m.nick else m.name}")
            members.append((m.id, m.name))

        for r in message.role_mentions:
            content = content.replace(f"<@&{r.id}>", f"@{r.name}")
            roles.append((r.id, r.name))

        for c in message.channel_mentions:
            content = content.replace(f"<#{c.id}>", f"#{c.name}")
            channels.append((c.id, c.name))

        return content, members, roles, channels

    # Checks

    def guild_check(self, guild):
        return guild.id in self.watched_guilds

    def channel_check(self, channel):
        return channel.id not in self.ignored_channels

    def dm_message_check(self, message):
        return isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel)

    def m_check(self, m):
        if self.watched_guilds and not self.dm_message_check(m):
            return self.guild_check(m.guild) and self.channel_check(m.channel)
        else:
            return False

    # Formatter functions

    def header(self, title, delim='?'):
        w = self.w
        head = f"[ {title}{' ' * abs((w % 2) - (len(title) % 2))} ]"
        wrap = f"{delim * ((w - len(head)) // 2)}"
        return f"{wrap}{head}{wrap}"

    def send_formatted_message(self, m, h, delim='?'):
        content, m_mentions, r_mentions, c_mentions = self.handle_mentions(m)
        a = m.author
        nl = '\n'
        extra = ""
        if m_mentions:
            extra += f"{self.header('MEMBER MENTIONS', delim)}\n" \
                     f"{nl.join([': '.join([str(i), n]) for i, n in m_mentions])}\n"
        if r_mentions:
            extra += f"{self.header('ROLE MENTIONS', delim)}\n" \
                     f"{nl.join([': '.join([str(i), n]) for i, n in r_mentions])}\n"
        if c_mentions:
            extra += f"{self.header('CHANNEL MENTIONS', delim)}\n" \
                     f"{nl.join([': '.join([str(i), n]) for i, n in c_mentions])}\n"
        if m.attachments:
            extra += f"{self.header('ATTACHMENTS', delim)}\n{nl.join([a.url for a in m.attachments])}\n"

        print(f"{a.name} | {a.id}{f' | {a.nick}' if a.nick else ''}\n{m.guild.name} | {m.guild.id}\n"
              f"#{m.channel.name} | {m.channel.id}\n{self.header(h, delim)}\n{content}\n{extra}{delim * self.w}\n")

    def send_formatted_member(self, m, h, delim='?'):
        print(f"{m.guild.name} | {m.guild.id}\n{self.header(h, delim)}\n{m.name} | {m.id}\n{delim * self.w}\n")

    def send_formatted_nick(self, b, a, h, delim='?'):
        print(f"{a.guild.name} | {a.guild.id}\n{self.header(h, delim)}\n{a.name} | {a.id}\nBEFORE: {b.nick}\n"
              f"AFTER:  {a.nick}\n{delim * self.w}\n")

    def send_formatted_roles(self, m, r, x, h, delim='?'):
        print(f"{m.guild.name} | {m.guild.id}\n{m.name} | {m.id}\n{self.header(h, delim)}\nROLE {x}: {r}\n"
              f"{delim * self.w}\n")

    # Listeners

    async def on_message(self, m):
        if self.m_check(m):
            self.send_formatted_message(m, 'NEW MSG', delim='=')

    async def on_message_edit(self, b, a):
        if self.m_check(a):
            self.send_formatted_message(a, 'MSG EDIT', delim='#')

    async def on_message_delete(self, m):
        if self.m_check(m):
            self.send_formatted_message(m, 'MSG DEL', delim='X')

    async def on_member_join(self, m):
        if self.guild_check(m.guild):
            self.send_formatted_member(m, 'MEMBER JOIN', delim='%')

    async def on_member_update(self, b, a):
        if self.guild_check(a.guild):
            if a.nick != b.nick:
                self.send_formatted_nick(b, a, 'NICK CHG', delim='@')
            if a.roles != b.roles:
                x, r = self.role_change(b, a)
                self.send_formatted_roles(a, r, x, 'ROLE CHG', delim='&')


@bot.event
async def on_ready():
    try:
        app_info = await bot.application_info()  # Bot Only
        bot.owner = discord.utils.get(bot.get_all_members(), id=app_info.owner.id)  # Bot only
    except:
        bot.owner = None
    bot.loop.create_task(init_timed_events(bot))
    bot.add_cog(Listeners(bot))
    await sleep(1)
    await bot.change_presence(status=discord.Status.idle, afk=True)


if __name__ == "__main__":
    try:
        bot.run(db.hget("selfbot:config:run", "token"), bot=False)
    except KeyboardInterrupt:
        bot.logout()
