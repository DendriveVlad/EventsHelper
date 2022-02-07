import os
from asyncio import sleep
from time import time

from discord import *
from discord_components import DiscordComponents
from discord.ext import tasks, commands

from DataBase import DB
from config import *

__author__ = "Vladi4ka | DendriveVlad"

db = DB()


class Bot(commands.Bot):
    async def on_ready(self):
        DiscordComponents(self)


client = Bot(command_prefix="/", intents=Intents.all())
client.remove_command("help")
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")
client.run(TOKEN)
