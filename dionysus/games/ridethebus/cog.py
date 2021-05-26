import logging
from typing import Dict

import discord
from discord.ext import commands

from .game import RideTheBus, GameState

logger = logging.getLogger(__name__)

COLOR = 0xFFFF00

ROUND_MESSAGES = {
    GameState.RED_OR_BLACK: "",
    GameState.HIGHER_OR_LOWER: "",
    GameState.INSIDE_OR_OUTSIDE: "",
    GameState.SUIT: "",
}


class RideTheBusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.keys: Dict[str, RideTheBus] = {}
        self.channels: Dict[discord.abc.Messageable, RideTheBus] = {}
        self.players: Dict[discord.User, RideTheBus] = {}

    @commands.group()
    async def bus(self, ctx: commands.Context):
        if ctx.invoked_subcommand is not None:
            return

        embed = discord.Embed(
            color=0x00FFFF,
            title="Ride The Bus",
            description="A card based drinking game.",
        )
        await ctx.send(embed=embed)

    @bus.command()
    async def create(self, ctx: commands.Context):
        if ctx.channel in self.channels:
            await ctx.reply(
                f"There is already a Ride The Bus game in progress here!\nUse `{self.bot.command_prefix}bus join {self.channels[ctx.channel].key}` to join."
            )
            return
        game = RideTheBus()
        self.channels[ctx.channel] = game
        self.keys[game.key] = game
        embed = discord.Embed(
            color=COLOR,
            title="Ride The Bus",
            description=f"Ride The Bus game created.\nUse `{self.bot.command_prefix}bus join {self.channels[ctx.channel].key}` to join.",
        )
        await ctx.send(embed=embed)

    @bus.command()
    async def join(self, ctx: commands.Context, key: str):
        if key not in self.keys:
            await ctx.reply(f"Sorry, there is no game with the key {key}...")
            return
        if key in self.players:
            game = self.players[ctx.author]
            await ctx.reply(f"Sorry, you're already in a game {game.key}.")
            return
        user = ctx.author
        game = self.keys[key]
        game.add_player(user.id, user.name)
        self.players[user] = game
        await ctx.reply(f"You have joined the game {game.key}!")

    @bus.command()
    async def leave(self, ctx: commands.Context):
        if ctx.author not in self.players:
            await ctx.reply(f"Sorry, you're not in any games you can leave...")
            return
        # Get a reference to the game
        game = self.players[ctx.author]
        # Remove the player from the game
        game.remove_player(ctx.author.id)
        # Remove the player from the player list
        self.players.pop(ctx.author)
        await ctx.reply(f"You have left the game {game.key}.")

    @bus.command()
    async def start(self, ctx: commands.Context):
        if ctx.author not in self.players:
            await ctx.reply(f"Sorry, you're not in any games you can start...")

    def _build_round_start(self, game: RideTheBus):
        embed = discord.Embed(color=COLOR, title="Ride The Bus", description=f"")
        return embed