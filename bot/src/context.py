from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from src.main import Client


class Context(discord.ApplicationContext):
    """Custom ApplicationContext."""

    async def error(self, message: str) -> None:
        """Send an ephemeral error message to the user."""
        try:
            embed = discord.Embed(description=message, colour=discord.Colour.red())

            await self.respond(embed=embed, ephemeral=True)

        except discord.HTTPException:
            pass


class AutocompleteContext(discord.AutocompleteContext):
    """Custom AutocompleteContext."""

    def __init__(self, bot: Client, interaction: discord.Interaction) -> None:
        super().__init__(bot, interaction)
