import asyncio
import os

import discord
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

from src.context import AutocompleteContext, Context
from src.wrapper.interface import Interface

load_dotenv(find_dotenv())

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID")
API_URL = os.environ["API_URL"]


class Client(commands.Bot):
    """Wrapper for the pycord client to store state."""

    def __init__(self, testing_guild_id: int | None = None) -> None:
        super().__init__(debug_guild_id=[testing_guild_id] if testing_guild_id else None)

        self.interface = Interface(address=API_URL, token="")

    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls=Context,  # pyright: ignore[reportMissingParameterType]  # noqa: ANN001
    ) -> discord.ApplicationContext:
        """Return custom application context."""
        return await super().get_application_context(interaction, cls)

    async def get_autocomplete_context(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        interaction: discord.Interaction,
        cls=AutocompleteContext,  # pyright: ignore[reportMissingParameterType]  # noqa: ANN001
    ) -> discord.AutocompleteContext:
        """Return custom autocomplete context."""
        return await super().get_autocomplete_context(interaction, cls)

    async def on_ready(self) -> None:
        """Ran after bot has logged in."""
        user = self.user

        if user is None:
            return

        print(f"Logged in as {user.name}({user.id})")


async def main() -> None:
    testing_guild_id = int(TESTING_GUILD_ID) if TESTING_GUILD_ID is not None else None

    client = Client(testing_guild_id=testing_guild_id)

    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            client.load_extension(f"src.cogs.{filename[:-3]}")

    await client.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
