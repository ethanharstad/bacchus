import asyncio
import logging
import random
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
        # Games keyed by player id
        self.players = {}

    def _build_hand_embed(self, game: CardsAgainstHumanity, player_id: int):
        judge: discord.User = self.bot.get_user(game.get_judge_id())
        player: Player = game.players[player_id]
        
        q = "\n".join(['> ' + s for s in game.question.split("\n")])
        prompt = f"Submit your answer with `{self.bot.command_prefix}cah submit {' '.join('[id]' for i in range(game.question.pick))}`"
        desc = f"Choose your best answer to:\n{q}\n{judge.name} will be judging.\n{prompt}"
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
            color=0xFF0000,
        )
        for i, answer in enumerate(hand):
            embed.add_field(name=i, value=str(answer), inline=False)

        await ctx.send(embed=embed)

    @cah.command(brief="Join an existing Cards Against Humanity game")
    async def join(self, ctx, key: str):
        if key not in self.games:
            pass
        user = ctx.author
        if user.id in self.players:
            pass
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
            pass

        key = self.players[user.id]
        if key not in self.games:
            pass
        ref = self.games[key]
        game = ref["game"]

        # The game requires you to be a member in order to start it
        if user.id not in game.players:
            await user.send(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because you haven't joined it.".format(
                    game=game, guild=ref["guild"], channel=ref["channel"]
                )
            )
            return False
        # The game requires at least 3 players
        if len(game.players) < 3:
            await user.send(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because it doesn't have enough players yet.".format(
                    game=game, guild=ref["guild"], channel=ref["channel"]
                )
            )
            return False

        # Start the game!
        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Started by {user.display_name}!",
            color=COLOR,
        )
        embed.set_footer(
            text="Cards Against Humanity game {game.key}".format(game=game)
        )
        await ref["channel"].send(embed=embed)
        return True

    @cah.command(brief="Submit an answer to a round of Cards Against Humanity")
    async def submit(self, ctx, *args):
        user = ctx.author
        if user.id not in self.players:
            await ctx.message.reply(f"Sorry, you're not part of the game!")
            return

        key = self.players[user.id]
        if key not in self.games:
            await ctx.message.reply(f"Sorry, I forgot which game you were playing... Try joining again?")
            return
        ref = self.games[key]
        game = ref["game"]

        if user.id not in game.players:
            pass
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
            await ctx.message.reply(f"You're the judge, you don't get to submit an answer!")
            return
        except ValueError:
            await ctx.message.reply(f"You don't need to submit an answer right now. Tryhard.")
            return
        except KeyError:
            await ctx.message.reply(f"Sorry, I forgot which game you were playing... Try joining again?")
            return
        except IndexError:
            await ctx.message.reply(f"Dummy, you need to submit {game.question.pick} answers!")
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
        if game.state == GameState.ROUND_COMPLETE:
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

        game.start_round()
        for player_id in game.players:
            user = self.bot.get_user(player_id)
            if player_id == game.get_judge_id():
                embed = discord.Embed(
                    title="Cards Against Humanity",
                    description=f"You will be judging the answers fo\n> {game.question}",
                    color=COLOR
                )
                await user.send(embed=embed)
                continue
            hand = self._build_hand_embed(game, player_id)
            await user.send(embed=hand)
