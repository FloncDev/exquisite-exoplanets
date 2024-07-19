import asyncio
import os

from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.environ["DISCORD_TOKEN"]
TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID")

client = commands.Bot()


@client.listen()
async def on_ready() -> None:
    user = client.user

    if user is None:
        return

    print(f"Logged in as {user.name}({user.id})")


async def main() -> None:
    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"src.cogs.{filename[:-3]}")

    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
