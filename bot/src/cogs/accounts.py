import discord
from discord import app_commands
from discord.ext import commands

from src.main import DiscordClient


class Accounts(commands.Cog):
    def __init__(self, client: DiscordClient) -> None:
        self.client = client

    @app_commands.command(name="profile")
    async def profile(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        """Get info about an account. Leave user blank to see your own."""
        if user is None:
            user = interaction.user

        if user.bot:
            # TODO: Make into a nicer embed
            await interaction.response.send_message("Bots can't have accounts!", ephemeral=True)
            return

        avatar = user.avatar
        if avatar:
            avatar = avatar.url

        embed = discord.Embed(title=f"{user.name}'s account")
        embed.set_thumbnail(url=avatar)

        await interaction.response.send_message(embed=embed)


async def setup(client: DiscordClient):
    await client.add_cog(Accounts(client))
