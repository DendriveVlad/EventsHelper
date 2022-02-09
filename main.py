import os
from asyncio import sleep
from time import time

from nextcord import *
from nextcord.ext import tasks, commands

from DataBase import DB
from config import *

__author__ = "Vladi4ka | DendriveVlad"

db = DB()


class Bot(commands.Bot):
    async def on_ready(self):
        for member in self.get_guild(GUILD_ID).members:
            if not (db.select("members", f"id == {member.id}") or member.id == MY_ID):
                db.insert("members", id=member.id, date_connection=time())
        print("Ready")

    async def on_member_join(self, member):
        if not db.select("members", f"id == {member.id}"):
            db.insert("members", id=member.id, date_connection=time())


client = Bot(command_prefix="/", intents=Intents.all())
client.remove_command("help")
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")
client.run(TOKEN)
