import asyncio
import logging
import random
from typing import Dict, List
import discord
from discord.ext import commands
import emoji

from .game import CardsAgainstHumanity, GameState, Player, ANSWERS, QUESTIONS

logger = logging.getLogger(__name__)

COLOR = 0x00FFFF


class CardsAgainstHumanityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        # A reference to the bot client
        self.bot = bot
        # Games keyed by game id
        self.games = {}
        # Games keyed by channel id
        self.channels: Dict[int, str] = {}
        # Games keyed by player id
        self.players: Dict[int, str] = {}

    def _get_game_for_player(self, player_id: int) -> CardsAgainstHumanity:
        key = self.players[player_id]
        return self.games[key]["game"]

    def _get_game_for_channel(self, channel_id: int) -> CardsAgainstHumanity:
        key = self.channels[channel_id]
        return self.games[key]["game"]

    def _build_hand_embed(self, game: CardsAgainstHumanity, player_id: int):
        judge: discord.User = self.bot.get_user(game.get_judge_id())
        player: Player = game.players[player_id]

        prompt = f"Submit your answer with `{self.bot.command_prefix}cah submit {' '.join('[id]' for i in range(game.question.pick))}`"
        desc = f"Choose your best answer to:\n{game.question.render()}\n{judge.name} will be judging.\n{prompt}"
        logger.info(f"Hand Desc: {desc}")

        embed = discord.Embed(
            title="Cards Against Humanity",
            description=desc,
            color=COLOR,
        )

        for i, answer in enumerate(player.hand):
            embed.add_field(name="{}".format(i + 1), value=str(answer), inline=False)

        return embed

    def _build_judge_embed(self, game: CardsAgainstHumanity):
        embed = discord.Embed(
            title="Cards Against Humanity",
            description=f"Choose the best answer to:\n{game.question}\nSelect the winner with `{self.bot.command_prefix}cah choose [id]`",
            color=COLOR,
        )
        for i, submission_id in enumerate(game.submission_mapping):
            answer = game.submissions[submission_id]
            embed.add_field(
                name=f"{i + 1}", value=game.question.fill_in(answer), inline=False
            )

        return embed

    def _build_winner_embed(self, game: CardsAgainstHumanity):
        winner = game.get_winner_id()
        submissions = sorted(game.submissions, key=lambda x: game.players[x].name)
        embed = discord.Embed(
            title="Cards Against Humanity",
            description=f"{game.players[game.get_judge_id()].name} chose {game.players[winner].name} as the winner!",
            color=COLOR,
        )
        embed.add_field(
            name=emoji.emojize(f":star: {game.players[winner].name} :star:"),
            value=game.question.fill_in(game.submissions[winner]),
            inline=False,
        )
        for player_id in submissions:
            # Skip the winner
            if player_id == winner:
                continue
            embed.add_field(
                name=game.players[player_id].name,
                value=game.question.fill_in(game.submissions[player_id]),
                inline=False,
            )
        return embed

    def _build_score_embed(self, game: CardsAgainstHumanity):
        ranks = sorted(game.players, key=lambda id: game.players[id].score)
        score_list = []
        for id in ranks:
            player = game.players[id]
            score_list.append(f"{player.name} - {player.score}")
        scores = "\n".join(score_list)
        embed = discord.Embed(
            title="Cards Against Humanity",
            description=f"Scores after {game.round} rounds:\n{scores}",
            color=COLOR,
        )
        return embed

    @commands.group(brief="Overview of Cards Against Humanity")
    async def cah(self, ctx):
        if ctx.invoked_subcommand is not None:
            return

        embed = discord.Embed(
            color=COLOR,
            title="Cards Against Humanity",
            description=f"An irreverant card game.\nUse `{self.bot.command_prefix}cah create` to form a game.",
        )
        await ctx.send(embed=embed)

    @cah.command(brief="Create a game of Cards Against Humanity")
    async def create(self, ctx: commands.Context):
        user = ctx.author
        if not ctx.guild:
            await ctx.send(
                "Sorry {user.display_name}, you can only play this game inside a server.".format(
                    user=user
                )
            )
            return False

        game = CardsAgainstHumanity()
        self.games[game.key] = {
            "guild": ctx.guild,
            "channel": ctx.channel,
            "game": game,
        }
        self.channels[ctx.channel.id] = game.key

        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Fill in the blank using politically incorrect words or phrases.",
            color=COLOR,
        )
        embed.set_footer(
            text="Game {game.key} created by {user.display_name}".format(
                user=user, game=game
            )
        )
        embed.add_field(
            name="{prefix}cah join {key}".format(
                prefix=self.bot.command_prefix, key=game.key
            ),
            value="to join",
            inline=True,
        )
        embed.add_field(
            name="{prefix}cah start {key}".format(
                prefix=self.bot.command_prefix, key=game.key
            ),
            value="to start",
            inline=True,
        )

        await ctx.send(embed=embed)
        return True

    @cah.command(hidden=True, brief="Deal a random Cards Against Humanity hand [DEBUG]")
    async def deal(self, ctx):
        hand = random.choices(ANSWERS, k=8)
        question = random.choice(QUESTIONS)
        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Chose the best answer for\n\n> {}".format(question),
            color=COLOR,
        )
        for i, answer in enumerate(hand):
            embed.add_field(name=i, value=str(answer), inline=False)

        await ctx.send(embed=embed)

    @cah.command(brief="Join an existing Cards Against Humanity game")
    async def join(self, ctx: commands.Context, key: str = None):
        user = ctx.author
        if key is None:
            try:
                game = self._get_game_for_channel(ctx.channel.id)
                ref = self.games[game.key]
            except:
                await ctx.message.reply(
                    "Sorry, you need to pass a game key or join from a channel."
                )
                return
        else:
            if key not in self.games:
                await ctx.message.reply("Sorry, that game key doesn't exist.")
                return
            if user.id in self.players:
                await ctx.message.reply(
                    "You're alredy in a game, leave it first before joining this one."
                )
                return
            ref = self.games[key]
            game = ref["game"]

        if game.add_player(Player(user.id, user.display_name)):
            self.players[user.id] = game.key
            await user.send(
                "Thanks for joining Cards Against Humanity game {game.key} in {guild.name} {channel.mention}.\nIt will start shortly.".format(
                    game=game, guild=ref["guild"], channel=ref["channel"]
                )
            )
        else:
            pass

    @cah.command(brief="Start a Cards Against Humanity game")
    async def start(self, ctx):
        user = ctx.author
        if user.id not in self.players:
            await ctx.message.reply("You need to join a game before you can start it.")
            return

        key = self.players[user.id]
        if key not in self.games:
            await ctx.message.reply(
                "Something seems to have gone wrong. Try joining a new game."
            )
            return
        ref = self.games[key]
        game = ref["game"]

        # The game requires you to be a member in order to start it
        if user.id not in game.players:
            await ctx.message.reply(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because you haven't joined it.".format(
                    game=game, guild=ref["guild"], channel=ref["channel"]
                )
            )
            return
        # The game requires at least 3 players
        if len(game.players) < 3:
            await ctx.message.reply(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because it doesn't have enough players yet.".format(
                    game=game, guild=ref["guild"], channel=ref["channel"]
                )
            )
            return

        # Start the game!
        embed = discord.Embed(
            title="Cards Against Humanity",
            description=f"Started by {user.display_name}!",
            color=COLOR,
        )
        embed.set_footer(text=f"Cards Against Humanity game {game.key}")
        await ref["channel"].send(embed=embed)

        await asyncio.sleep(5)
        await self._play_round(game)

    @cah.command(brief="Stop a Cards Against Humanity game")
    async def stop(self, ctx):
        # TODO stop the game
        pass

    @cah.command(brief="Submit an answer to a round of Cards Against Humanity")
    async def submit(self, ctx, *args):
        user = ctx.author
        if user.id not in self.players:
            await ctx.message.reply("Sorry, you're not part of any games!")
            return

        key = self.players[user.id]
        if key not in self.games:
            await ctx.message.reply(
                "Sorry, I forgot which game you were playing... Try joining again?"
            )
            return
        ref = self.games[key]
        game = ref["game"]

        if user.id not in game.players:
            await ctx.message.reply(
                "You're not part of the game so you can't start it."
            )
            return
        player = game.players[user.id]

        answers = []
        for i in args:
            j = int(i)
            a = player.hand[j - 1]
            answers.append(a)

        logger.info("Submit: {}".format(answers))
        try:
            game.submit_answer(player, answers)
        except AssertionError:
            await ctx.message.reply(
                f"You're the judge, you don't get to submit an answer!"
            )
            return
        except ValueError:
            await ctx.message.reply(
                f"You don't need to submit an answer right now. Tryhard."
            )
            return
        except KeyError:
            await ctx.message.reply(
                f"Sorry, I forgot which game you were playing... Try joining again?"
            )
            return
        except IndexError:
            await ctx.message.reply(
                f"Dummy, you need to submit {game.question.pick} answers!"
            )
            return
        logger.info("Submit: {}".format(game.question.fill_in(answers)))
        await user.send("You played:\n> {}".format(game.question.fill_in(answers)))

        # Check if the game is ready to judge
        if game.state == GameState.WAITING_FOR_JUDGE:
            await self._judging(game)

    async def _judging(self, game):
        embed = self._build_judge_embed(game)
        judge = self.bot.get_user(game.get_judge_id())
        await judge.send(embed=embed)

    @cah.command(brief="Choose the winning answer to a round of Cards Against Humanity")
    async def choose(self, ctx, answer_id: int):
        user = ctx.author
        if user.id not in self.players:
            return

        key = self.players[user.id]
        if key not in self.games:
            return
        ref = self.games[key]
        game = ref["game"]

        if user.id is not game.get_judge_id():
            return

        game.choose_winner(answer_id - 1)
        if game.state in [GameState.ROUND_COMPLETE, GameState.GAME_OVER]:
            channel = ref["channel"]

            winner_embed = self._build_winner_embed(game)
            await channel.send(embed=winner_embed)
            for player_id in game.players:
                user = self.bot.get_user(player_id)
                if player_id == game.get_judge_id():
                    await user.send(embed=winner_embed)

            score_embed = self._build_score_embed(game)
            await channel.send(embed=score_embed)
            for player_id in game.players:
                user = self.bot.get_user(player_id)
                await user.send(embed=score_embed)

        if game.state == GameState.GAME_OVER:
            # End the game
            return

        # Continue to the next round
        await asyncio.sleep(5)
        await self._play_round(game)

    async def _play_round(self, game: CardsAgainstHumanity):
        game.start_round()
        for player_id in game.players:
            user = self.bot.get_user(player_id)
            if player_id == game.get_judge_id():
                embed = discord.Embed(
                    title="Cards Against Humanity",
                    description=f"You will be judging the answers for\n> {game.question}",
                    color=COLOR,
                )
                await user.send(embed=embed)
                continue
            hand = self._build_hand_embed(game, player_id)
            await user.send(embed=hand)

    @cah.command(brief="Start a round of Cards Against Humanity [DEBUG]")
    async def debug(self, ctx):
        user = ctx.author
        if user.id not in self.players:
            return
        key = self.players[user.id]

        if key not in self.games:
            return
        ref = self.games[key]
        game = ref["game"]

        await self._play_round(game)
