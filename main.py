from discord.ext import commands
from asyncio import sleep
import discord
import sys
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

    def check_update(self):
        self.watched_guilds = [int(g) for g in list(db.smembers("eagleeye:watched_guilds"))]
        print(f"Guilds list updated: {', '.join([str(g) for g in self.watched_guilds])}")
        self.ignored_channels = [int(c) for c in list(db.smembers("eagleeye:ignored_channels"))]
        print(f"Ignored channels list updated: {', '.join([str(c) for c in self.ignored_channels])}\n")

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

    # Formatter functions

    def formatted_message(self, m, delim='?'):
        a = m.author
        return f"{a.name} | {a.id}{f' | {a.nick}' if a.nick else ''}\n{m.guild.name} | {m.guild.id}\n" \
               f"#{m.channel.name} | {m.channel.id}\n{delim*80}\n{m.content}\n{delim*80}\n"

    def formatted_member(self, m, delim='?'):
        return f"{m.guild.name} | {m.guild.id}\n{delim*80}\n{m.name} | {m.id}\n{delim*80}\n"

    def formatted_nick(self, b, a, delim='?'):
        return f"{a.guild.name} | {a.guild.id}\n{delim*80}\n{a.name} | {a.id}\nBEFORE: {b.nick}\nAFTER:  " \
               f"{a.nick}\n{delim*80}"

    def formatted_roles(self, m, r, x, delim='?'):
        return f"{m.guild.name} | {m.guild.id}\n{m.name} | {m.id}\n{delim*80}\nROLE {x}: {r}\n{delim*80}\n"

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

    # Listeners

    async def on_message(self, m):
        if self.m_check(m):
            print(f"NEW MSG | {self.formatted_message(m, delim='=')}")

    async def on_message_edit(self, b, a):
        if self.m_check(a):
            print(f"MSG EDIT | {self.formatted_message(a, delim='#')}")

    async def on_message_delete(self, m):
        if self.m_check(m):
            print(f"MSG DEL | {self.formatted_message(m, delim='X')}")

    async def on_member_join(self, m):
        if self.guild_check(m.guild):
            print(f"MEMBER JOIN | {self.formatted_member(m, delim='%')}")

    async def on_member_update(self, b, a):
        if self.guild_check(a.guild):
            if a.nick != b.nick:
                print(f"NICK CHG | {self.formatted_nick(b, a, delim='@')}")
            if a.roles != b.roles:
                x, r = self.role_change(b, a)
                print(f"ROLE CHG | {self.formatted_roles(a, r, x, delim='&')}")


@bot.event
async def on_ready():
    bot.loop.create_task(init_timed_events(bot))
    bot.add_cog(Listeners(bot))
    print("Started successfully.\n")


if __name__ == "__main__":
    bot.run(db.hget("selfbot:config:run", "token"), bot=False)
