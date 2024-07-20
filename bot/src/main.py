import asyncio
import os

import discord
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.environ["DISCORD_TOKEN"]
TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID")


class DiscordClient(commands.Bot):
    """Main class for the discord client."""

    def __init__(self, *, intents: discord.Intents, testing_guild_id: int | None = None) -> None:
        super().__init__("", intents=intents)
        self.testing_guild_id = testing_guild_id

    async def setup_hook(self) -> None:
        """Ran when setting up the bot, loads cogs."""
        for filename in os.listdir("./src/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        """Ran when bot has logged in."""
        user = self.user

        if user is None:
            return

        # TODO: Setup propper logging
        print(f"Logged in as {user.name}({user.id})")


async def main() -> None:
    discord.utils.setup_logging()

    bot = DiscordClient(
        intents=discord.Intents.default(),
        testing_guild_id=int(TESTING_GUILD_ID) if TESTING_GUILD_ID else None,
    )
    await bot.start(TOKEN)


asyncio.run(main())
