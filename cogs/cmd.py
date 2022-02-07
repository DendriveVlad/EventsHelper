from nextcord import *
from nextcord.ext import commands

from config import *
from DataBase import DB


class CMD(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @slash_command(name="create", description="Создать ивент", guild_ids=[GUILD_ID])
    async def create(self, interaction: Interaction, event_name):
        await interaction.response.send_message("Ивент будет создан")

    @slash_command(name="hello", description="said you hi", guild_ids=[GUILD_ID])
    async def hello(self, interaction, message:str):
        await interaction.response.send_message("hi", message)


def setup(client):
    client.add_cog(CMD(client))
