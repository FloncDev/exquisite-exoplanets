import discord
from discord.commands import SlashCommandGroup, option
from discord.ext import commands, pages

from src.context import AutocompleteContext, Context
from src.main import Client
from src.wrapper import ShopItem


async def item_autocomplete(_: AutocompleteContext) -> list[str]:
    # TODO: Change onces wrapper is fixed
    shop = [ShopItem(id=i, name=f"Item {i+1}", price=10, quantity=10) for i in range(10)]

    return [item.name for item in shop]


class Shop(commands.Cog):
    """Cog holding everything related to the shop."""

    def __init__(self, client: Client) -> None:
        self.client = client

    shop = SlashCommandGroup("shop")

    @shop.command()
    async def view(self, ctx: Context) -> None:
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

        paginator = pages.Paginator(
            pages=shop_pages  # pyright: ignore[reportArgumentType]
        )
        await paginator.respond(ctx.interaction)

    @shop.command()
    @option(
        "item",
        str,
        description="The item you want to buy.",
        autocomplete=item_autocomplete,
    )
    @option("quantity", int, description="How many you want to buy, defaults to 1.")
    async def buy(self, ctx: Context, item: str, quantity: int = 1) -> None:
        """Buy an item in the shop."""


def setup(client: Client) -> None:
    client.add_cog(Shop(client))
