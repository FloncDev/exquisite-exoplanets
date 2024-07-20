import discord
from discord import option
from discord.ext import commands

from src.context import Context


class Accounts(commands.Cog):
    """Cog to handle basic account functions."""

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.slash_command()
    @option("user", description="User's profile to check. Leave blank to see your own.")
    async def profile(
        self,
        ctx: Context,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        """Get info about an account. Leave user blank to see your own."""
        if user is None:
            user = ctx.author

        if user.bot:
            await ctx.error("You cannot view a bot profile")
            return

        avatar = user.avatar
        # If avatar is None, embed.set_thumbnail(url=None) will not set a thumbnail
        if avatar:
            avatar = avatar.url

        embed = discord.Embed(title=f"{user.name}'s account")
        embed.set_thumbnail(url=avatar)

        await ctx.respond(embed=embed)


def setup(client: commands.Bot) -> None:
    client.add_cog(Accounts(client))
