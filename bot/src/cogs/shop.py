import discord
from discord.ext import commands, pages

from src.context import Context
from src.main import Client
from src.wrapper import ShopItem


class Shop(commands.Cog):
    """Cog holding everything related to the shop."""

    def __init__(self, client: Client) -> None:
        self.client = client

    @commands.slash_command()
    async def shop(self, ctx: Context) -> None:
        """Interact with the shop."""
        # Temporary while wrapper is getting fixed
        shop = [ShopItem(id=i, name=f"Item {i+1}", price=10, quantity=10) for i in range(10)]

        shop_pages: list[discord.Embed] = []

        for index, item in enumerate(shop):
            if index % 6 == 0:
                shop_pages.append(
                    discord.Embed(
                        title="Shop",
                        description="`/shop buy <name>` to buy an item",
                    )
                )

            disabled_tag = "~~" if item.quantity == 0 else ""

            shop_pages[-1].add_field(
                name=f"{disabled_tag}{item.name}{disabled_tag}",
                value=f"${item.price:.2f}\n{item.quantity} in stock",
            )

        paginator = pages.Paginator(pages=shop_pages)  # pyright: ignore[reportArgumentType]
        await paginator.respond(ctx.interaction)


def setup(client: Client) -> None:
    client.add_cog(Shop(client))
