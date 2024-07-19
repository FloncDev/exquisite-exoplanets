import discord
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, client: discord.Bot) -> None:
        self.client = client

    @commands.slash_command(name="ping")
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        """Ping the bot"""
        await ctx.respond("pong")


def setup(client: discord.Bot):
    client.add_cog(Ping(client))
