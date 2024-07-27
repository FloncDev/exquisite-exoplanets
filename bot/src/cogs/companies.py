import re

import discord
from discord.commands import SlashCommandGroup, option
from discord.ext import commands

from src.context import Context
from src.main import Client
from src.wrapper.error import DoesNotExistError


class Companies(commands.Cog):
    """Cog containing commands related to company management."""

    def __init__(self, client: Client) -> None:
        self.client = client

    company = SlashCommandGroup("company", "Various commands to do with companyies")

    @company.command()
    @option("name", str, description="The name of your new company")
    async def create(self, ctx: Context, name: str) -> None:
        """Create a new company."""
        # Create an account if they do not have one
        try:
            await self.client.interface.user.get_user(ctx.author.id)
        except DoesNotExistError:
            await self.client.interface.user.register_user(ctx.author.id)

        if not re.match(r"^[a-zA-Z0-9\- \.]{1,}$", name):
            await ctx.error("Company name must only contain alphanumerics, spaces, `-` and `.`")
            return

        try:
            company = await self.client.interface.company.get_company(ctx.author.id)
        except DoesNotExistError:
            company = None

        if company:
            await ctx.error("You already have a company")
            return

        await ctx.defer(ephemeral=True)

        company = await self.client.interface.company.create_company(ctx.author.id, name)

        await ctx.respond("Company created", ephemeral=True)

        embed = discord.Embed(
            title="Company Founded!",
            # TODO: Use company.name once pushed to main
            description=f"{ctx.author.mention} has incorporated `{company.name}`",
            colour=discord.Colour.green(),
        )
        await ctx.send(embed=embed)

    @company.command()
    async def info(self, ctx: Context) -> None:
        """Get information about your company."""
        try:
            company = await self.client.interface.company.get_company(ctx.author.id)
        except DoesNotExistError:
            await ctx.error("You do not have a company! Please run `/company create`.")
            return

        embed = discord.Embed(title=f"Company Information: `{company.name}`")

        founder = await self.client.fetch_user(company.owner_id)
        embed.add_field(name="Founder", value=founder.mention, inline=True)

        net_worth = f"${company.current_networth:,}" if not company.is_bankrupt else "**Bankrupt**"
        embed.add_field(name="Net Worth", value=net_worth, inline=True)

        # creation_timestamp = int(datetime.fromisoformat(company.).timestamp())
        creation_timestamp = int(company.created_date.timestamp())
        embed.add_field(name="Creation Time", value=f"<t:{creation_timestamp}>")

        await ctx.respond(embed=embed)


def setup(client: Client) -> None:
    client.add_cog(Companies(client))
