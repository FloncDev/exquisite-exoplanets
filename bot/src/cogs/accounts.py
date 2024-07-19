import discord
from discord import option
from discord.ext import commands


class Accounts(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.slash_command()
    @option("user", description="User's profile to check. Leave blank to see your own.")
    async def profile(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        """Get info about an account. Leave user blank to see your own."""

        if user is None:
            user = ctx.author

        avatar = user.avatar
        if avatar:
            avatar = avatar.url

        embed = discord.Embed(title=f"{user.name}'s account")
        embed.set_thumbnail(url=avatar)

        await ctx.respond(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Accounts(client))
