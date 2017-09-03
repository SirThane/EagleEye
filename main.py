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

    # Utility functions

    @property
    def w(self):
        return shutil.get_terminal_size((80, 25)).columns

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

    def formatted_message(self, m, h, delim='?'):
        a = m.author
        nl = '\n'
        if m.attachments:
            atch = f"{self.header('ATTACHMENTS', delim)}\n{nl.join([a.url for a in m.attachments])}\n"
        else:
            atch = ""
        print(f"{a.name} | {a.id}{f' | {a.nick}' if a.nick else ''}\n{m.guild.name} | {m.guild.id}\n"
              f"#{m.channel.name} | {m.channel.id}\n{self.header(h, delim)}\n{m.content}\n{atch}{delim * self.w}\n")

    def formatted_member(self, m, h, delim='?'):
        print(f"{m.guild.name} | {m.guild.id}\n{self.header(h, delim)}\n{m.name} | {m.id}\n{delim * self.w}\n")

    def formatted_nick(self, b, a, h, delim='?'):
        print(f"{a.guild.name} | {a.guild.id}\n{self.header(h, delim)}\n{a.name} | {a.id}\nBEFORE: {b.nick}\n"
              f"AFTER:  {a.nick}\n{delim * self.w}\n")

    def formatted_roles(self, m, r, x, h, delim='?'):
        print(f"{m.guild.name} | {m.guild.id}\n{m.name} | {m.id}\n{self.header(h, delim)}\nROLE {x}: {r}\n"
              f"{delim * self.w}\n")

    # Listeners

    async def on_message(self, m):
        if self.m_check(m):
            self.formatted_message(m, 'NEW MSG', delim='=')

    async def on_message_edit(self, b, a):
        if self.m_check(a):
            self.formatted_message(a, 'MSG EDIT', delim='#')

    async def on_message_delete(self, m):
        if self.m_check(m):
            self.formatted_message(m, 'MSG DEL', delim='X')

    async def on_member_join(self, m):
        if self.guild_check(m.guild):
            self.formatted_member(m, 'MEMBER JOIN', delim='%')

    async def on_member_update(self, b, a):
        if self.guild_check(a.guild):
            if a.nick != b.nick:
                self.formatted_nick(b, a, 'NICK CHG', delim='@')
            if a.roles != b.roles:
                x, r = self.role_change(b, a)
                self.formatted_roles(a, r, x, 'ROLE CHG', delim='&')


@bot.event
async def on_ready():
    bot.loop.create_task(init_timed_events(bot))
    bot.add_cog(Listeners(bot))
    print("Started successfully.\n")


if __name__ == "__main__":
    try:
        bot.run(db.hget("selfbot:config:run", "token"), bot=False)
    except KeyboardInterrupt:
        bot.logout()
