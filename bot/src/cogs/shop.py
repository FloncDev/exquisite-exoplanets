from typing import TYPE_CHECKING

import discord
from discord.commands import SlashCommandGroup, option
from discord.ext import commands, pages

from src.context import AutocompleteContext, Context
from src.main import Client
from src.wrapper.error import DoesNotExistError, UserError

if TYPE_CHECKING:
    from src.wrapper.schema import ShopItem


async def item_autocomplete(ctx: AutocompleteContext) -> list[str]:
    shop = (
        ctx.bot.interface.shop.iter_items()  # pyright: ignore[reportAttributeAccessIssue]
    )

    return [item.name async for item in shop]


class Confirm(discord.ui.View):
    """Discord view with confirm/cancel buttons."""

    def __init__(self) -> None:
        super().__init__()
        self.confirmed = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(
        self,
        _,  # noqa: ANN001
        interaction: discord.Interaction,
    ) -> None:
        """Ran when confirm button is pressed."""
        await interaction.response.defer()
        self.confirmed = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(
        self,
        _,  # noqa: ANN001
        interaction: discord.Interaction,
    ) -> None:
        """Ran when cancel button is pressed."""
        await interaction.response.defer()
        self.confirmed = False
        self.stop()


class Shop(commands.Cog):
    """Cog holding everything related to the shop."""

    def __init__(self, client: Client) -> None:
        self.client = client

    shop = SlashCommandGroup("shop")

    @shop.command()
    async def view(self, ctx: Context) -> None:
        """Interact with the shop."""
        # Temporary while wrapper is getting fixed
        shop = self.client.interface.shop.iter_items()

        shop_pages: list[discord.Embed] = []

        # Yes, I know about enumerate but apparently it doesnt work with async generators
        index = 0
        async for item in shop:
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
            index += 1

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
        try:
            company = await self.client.interface.company.get_company(ctx.author.id)
        except DoesNotExistError:
            await ctx.error("You do not have a company.")
            return

        shop = self.client.interface.shop.iter_items()
        shop_item: ShopItem | None = None

        async for i in shop:
            if i.name == item:
                shop_item = i
                break

        if shop_item is None:
            await ctx.error("Could not find item.")
            return

        message = f"{quantity} `{item}`s for ${shop_item.price * quantity:.2f}"

        embed = discord.Embed(title="Confirmation", description=f"Are you sure you want to buy {message}")

        view = Confirm()

        await ctx.respond(embed=embed, view=view)

        await view.wait()

        if view.confirmed is None or not view.confirmed:
            embed.colour = discord.Colour.red()
            await ctx.edit(embed=embed, view=None)
            return

        try:
            await self.client.interface.shop.purchase(shop_item, company, quantity)
        except UserError:
            await ctx.error("Your company does not have enough money.")
            return

        embed.colour = discord.Colour.green()
        embed.title = "Shop Purchase"
        embed.description = f"Purchased {message}"
        await ctx.edit(embed=embed, view=None)


def setup(client: Client) -> None:
    client.add_cog(Shop(client))
