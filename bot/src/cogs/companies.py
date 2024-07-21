import asyncio
import re

import discord
from discord.commands import SlashCommandGroup, option
from discord.ext import commands

from src.context import Context


class Companies(commands.Cog):
    """Cog containing commands related to company management."""

    def __init__(self, client: discord.Bot) -> None:
        self.client = client

    company = SlashCommandGroup("company", "Various commands to do with companyies")

    @company.command()
    @option("name", str, description="The name of your new company")
    async def create(self, ctx: Context, name: str) -> None:
        """Create a new company."""
        if not re.match(r"^[a-zA-Z0-9\- \.]{1,}$", name):
            await ctx.error("Company name must only contain alphanumerics, spaces, `-` and `.`")
            return

        # TODO: Make API requests
        has_company = False

        if has_company:
            await ctx.error("You already have a company")
            return

        await ctx.defer(ephemeral=True)

        # Emulate creating company
        await asyncio.sleep(0.5)

        await ctx.respond("Company created", ephemeral=True)

        embed = discord.Embed(
            title="Company Founded!",
            description=f"{ctx.author.mention} has incorporated `{name}`",
            colour=discord.Colour.green(),
        )
        await ctx.send(embed=embed)

    @company.command()
    async def view(self, ctx: Context) -> None:
        """Get information about a company."""
        await ctx.respond("TODO")


def setup(client: discord.Bot) -> None:
    client.add_cog(Companies(client))
