import os

import discord
from discord.ext import commands

bot_prefix = os.getenv("PREFIX") or "p."

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(bot_prefix),  # type: ignore
    intents=discord.Intents.all(),
    case_insensitive=False,
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Missing Token")


async def load_all_extensions() -> None:
    for filename in os.listdir("./ext"):
        if filename.endswith(".py"):
            await bot.load_extension(f"ext.{filename[:-3]}")


@bot.event
async def setup_hook() -> None:
    await load_all_extensions()


@bot.event
async def on_ready() -> None:
    print("------------------------------------")
    print(f"Bot Name: {bot.user.name}")  # type: ignore
    print(f"Bot ID: {bot.user.id}")  # type: ignore
    print(f"Guilds: {len(bot.guilds)}")
    print("------------------------------------")


@bot.command("sync")
async def sync_command(ctx: commands.Context) -> None:  # type: ignore[reportMissingTypeArgument]
    app_cmds = await bot.tree.sync()
    await ctx.reply(
        embed=discord.Embed(
            title=f"Synced {len(app_cmds)} cmd",
            description="\n".join([f"- {app_cmd.name}({app_cmd.id})" for app_cmd in app_cmds]),
        ),
    )


bot.run(TOKEN)
