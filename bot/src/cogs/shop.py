import discord
from discord.ext import commands


class Shop(commands.Cog):
    """Cog holding everything related to the shop."""

    def __init__(self, client: discord.Bot) -> None:
        self.client = client

    @commands.slash_command()
    async def shop(self, ctx: discord.ApplicationContext) -> None:
        """Interact with the shop."""
        await ctx.respond("TODO")


def setup(client: discord.Bot) -> None:
    client.add_cog(Shop(client))
