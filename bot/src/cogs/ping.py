import discord
from discord import app_commands
from discord.ext import commands

from src.main import DiscordClient


class Ping(commands.Cog):
    def __init__(self, client: DiscordClient) -> None:
        self.client = client

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Ping the bot"""
        await interaction.response.send_message("Pong")


async def setup(client: DiscordClient):
    await client.add_cog(Ping(client))
