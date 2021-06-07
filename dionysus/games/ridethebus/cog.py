import logging
from typing import Dict, List, Iterable
import asyncio

import discord
from discord.ext import commands
import emoji

from .game import RideTheBus, GameState
from .result import Result
from utils import playingcards

logger = logging.getLogger(__name__)

COLOR = 0xFFFF00

ROUND_RULES = {
    GameState.RED_OR_BLACK: "Answer the questions to build your hand, drinking along the way.",
    GameState.PYRAMID: "Play your matching cards to force others to drink.",
    GameState.RIDE_THE_BUS: "The loser has to ride the bus, and drink. A lot.",
}

ROUND_MESSAGES = {
    GameState.RED_OR_BLACK: {
        "prompt": emoji.emojize(":red_square: Red or :black_large_square: Black?"),
        "reactions": {
            emoji.emojize(":red_square:"): "red",
            emoji.emojize(":black_large_square:"): "black",
        },
    },
    GameState.HIGHER_OR_LOWER: {
        "prompt": emoji.emojize(":arrow_up: Higher or :arrow_down: Lower?"),
        "reactions": {
            "⬆️": "higher",
            "⬇️": "lower",
        },
    },
    GameState.INSIDE_OR_OUTSIDE: {
        "prompt": emoji.emojize(":thumbsup: Inside or :thumbsdown: Outside?"),
        "reactions": {
            "👍": "inside",
            "👎": "outside",
        },
    },
    GameState.SUIT: {
        "prompt": emoji.emojize(
            ":clubs: Club, :diamonds: Diamond, :hearts: Heart, or :spades: Spade?"
        ),
        "reactions": {
            "♣️": "clubs",
            "♦️": "diamonds",
            "♥️": "hearts",
            "♠️": "spades",
        },
    },
}


class RideTheBusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.keys: Dict[str, RideTheBus] = {}
        self.channels: Dict[discord.abc.Messageable, RideTheBus] = {}
        self.players: Dict[discord.User, RideTheBus] = {}
        self.context: Dict[str, discord.Context] = {}
        self.msg_refs: Dict[discord.Message, RideTheBus] = {}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # Ignore reactions from the bot
        if user.bot:
            return
        # Try to get the game this reaction is for
        try:
            game = self.msg_refs[reaction.message]
        except:
            logger.warning(f"Failed to get game for {reaction} by {user}")
            return
        # Validate the reaction
        if not self._validate_reaction(game, reaction, user):
            # Remove the invalid reaction
            await reaction.message.remove_reaction(reaction, user)
            return
        logger.info(f"Processing {reaction} by {user} in {game.key}")
        result = game.guess(
            user.id, ROUND_MESSAGES[game.state]["reactions"][reaction.emoji]
        )
        embed = self._build_result(game, result)
        ctx = self.context[game.key]
        await ctx.send(embed=embed)

        self.msg_refs.pop(reaction.message)
        await asyncio.sleep(3)
        await self._handle_state(game)

    def _build_result(self, game: RideTheBus, result: Result):
        user = self.bot.get_user(result.player.id)
        card = result.player.cards[-1]
        result = "WON" if result.successful else "LOST"
        embed = discord.Embed(
            color=COLOR, title="Ride The Bus", description=f"Drew {card} and {result}"
        )
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        embed.set_image(url=playingcards.get_card_image_url(card))
        return embed

    def _validate_reaction(
        self, game: RideTheBus, reaction: discord.Reaction, user: discord.User
    ):
        if user.id is not game.current_player.id:
            return False
        try:
            if reaction.emoji not in ROUND_MESSAGES[game.state]["reactions"]:
                return False
        except:
            return False
        return True

    async def _handle_state(self, game: RideTheBus):
        if game.state in [GameState.INIT, GameState.COMPLETE]:
            return
        await self._send_prompt(game)

    @commands.group(brief="Overview of Ride The Bus")
    async def bus(self, ctx: commands.Context):
        if ctx.invoked_subcommand is not None:
            return

        embed = discord.Embed(
            color=COLOR,
            title="Ride The Bus",
            description="A card based drinking game.",
        )
        await ctx.send(embed=embed)

    @bus.command(brief="Create a game of Ride The Bus")
    async def create(self, ctx: commands.Context):
        if ctx.channel in self.channels:
            await ctx.reply(
                f"There is already a Ride The Bus game in progress here!\nUse `{self.bot.command_prefix}bus join {self.channels[ctx.channel].key}` to join."
            )
            return
        game = RideTheBus()
        self.channels[ctx.channel] = game
        self.keys[game.key] = game
        self.context[game.key] = ctx
        embed = discord.Embed(
            color=COLOR,
            title="Ride The Bus",
            description=f"Ride The Bus game created.\nUse `{self.bot.command_prefix}bus join {self.channels[ctx.channel].key}` to join.",
        )
        await ctx.send(embed=embed)

    @bus.command(brief="Join an existing game of Ride The Bus")
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

    @bus.command(brief="Leave your game of Ride The Bus")
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

    @bus.command(brief="Start a game of Ride The Bus")
    async def start(self, ctx: commands.Context):
        if ctx.author not in self.players:
            await ctx.reply(f"Sorry, you're not in any games you can start...")
        game = self.players[ctx.author]
        game.start()
        embed = self._build_round_start(game)
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await self._send_prompt(game)

    def _build_round_start(self, game: RideTheBus):
        player_list = self._build_player_list(game)
        embed = discord.Embed(
            color=COLOR,
            title="Ride The Bus",
            description=f"{ROUND_RULES.get(game.state, '')}\n\nPlayers:\n{player_list}",
        )
        return embed

    async def _send_prompt(self, game: RideTheBus):
        ctx = self.context[game.key]
        user = self.bot.get_user(game.current_player.id)
        embed = self._build_prompt(game, user)
        msg = await ctx.send(embed=embed)
        await self._add_reactions(msg, ROUND_MESSAGES[game.state]["reactions"].keys())
        self.msg_refs[msg] = game

    def _build_prompt(self, game: RideTheBus, user: discord.User):
        prompt = ROUND_MESSAGES[game.state]["prompt"]
        embed = discord.Embed(color=COLOR, title="Ride The Bus", description=prompt)
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        return embed

    def _build_player_list(self, game: RideTheBus):
        s = ""
        for i, player in enumerate(game.player_list):
            s += f"{i+1}: {player.name}\n"
        return s

    async def _add_reactions(self, msg: discord.Message, reactions: Iterable[str]):
        for reaction in reactions:
            await msg.add_reaction(reaction)
