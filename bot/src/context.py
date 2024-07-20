import discord


class Context(discord.ApplicationContext):
    """Custom ApplicationContext."""

    async def error(self, message: str) -> None:
        """Send an ephemeral error message to the user."""
        try:
            embed = discord.Embed(description=message)

            await self.respond(embed=embed, ephemeral=True)

        except discord.HTTPException:
            pass
