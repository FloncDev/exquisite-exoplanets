from discord.ext import commands

from src.context import Context
from src.main import Client


class Planet(commands.Cog):
    """Cog related to planet commands."""

    def __init__(self, client: Client) -> None:
        self.client = client

    @commands.slash_command()
    async def planet(self, ctx: Context) -> None:
        """Ping the bot."""
        await ctx.respond("pong")


def setup(client: Client) -> None:
    client.add_cog(Planet(client))
