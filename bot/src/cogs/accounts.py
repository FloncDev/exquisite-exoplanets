import discord
from discord import option
from discord.ext import commands

from src.context import Context


class Accounts(commands.Cog):
    """Cog to handle basic account functions."""

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.XP_BAR_WIDTH = 15  # Width of XP bar in chars

    @commands.slash_command()
    @option(
        "user",
        discord.User | discord.Member,
        description="User's profile to check. Leave blank to see your own.",
        required=False,
    )
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

        # TODO: Use API calls once they have been implemented
        # For now, it's just dummy data
        level = 10
        experience = 123
        experience_needed = 200

        progress = int((experience / experience_needed) * self.XP_BAR_WIDTH)
        progress_needed = self.XP_BAR_WIDTH - progress

        level_text = f"**Level**: {level}\n"
        level_text += f"**XP**: {experience} / {experience_needed}\n"
        level_text += f"[{"="*progress}{"-"*progress_needed}]"

        embed.add_field(name="Account Level", value=level_text, inline=True)

        company = "Mining Inc."

        embed.add_field(name="Current Company", value=company, inline=True)

        await ctx.respond(embed=embed)


def setup(client: commands.Bot) -> None:
    client.add_cog(Accounts(client))
