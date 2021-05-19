import logging
import random
import discord
from discord.ext import commands

from .game import CardsAgainstHumanity, Player, ANSWERS, QUESTIONS

logger = logging.getLogger(__name__)


class CardsAgainstHumanityCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        # A reference to the bot client
        self.bot = bot 
        # Games keyed by game id
        self.games = {}
        # Games keyed by player id
        self.players = {}

    def _build_hand_embed(self, game: CardsAgainstHumanity, player_id: int):
        player: Player = game.players[player_id]

        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Choose your best answer to:\n{}".format(game.question),
            color=0x00FFFF,
        )

        for i, answer in enumerate(player.hand):
            embed.add_field(name="{}".format(i + 1), value=str(answer), inline=False)

        return embed


    def _build_judge_embed(self, game: CardsAgainstHumanity):
        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Choose the best answer to:\n{}".format(game.question),
            color=0x00FFF,
        )

        for i, answer in enumerate(random.shuffle(game.submissions.values())):
            embed.add_field(name="{}".format(i + 1), value=", ".join(answer), inline=False)

        return embed


    @commands.group()
    async def cah(self, ctx):
        # async def cah(ctx, user: discord.User = None):
        if ctx.invoked_subcommand is None:
            # user = user or ctx.author
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
                'guild': ctx.guild,
                'channel': ctx.channel,
                'game': game,
            }

            embed = discord.Embed(
                title="Cards Against Humanity",
                description="Fill in the blank using politically incorrect words or phrases.",
                color=0x00FFFF,
            )
            embed.set_footer(
                text="Game {game.key} created by {user.display_name}".format(
                    user=user, game=game
                )
            )
            embed.add_field(name="{prefix}cah join {key}".format(prefix=self.bot.command_prefix, key=game.key), value="to join", inline=True)
            embed.add_field(name="{prefix}cah start {key}".format(prefix=self.bot.command_prefix, key=game.key), value="to start", inline=True)

            await ctx.send(embed=embed)
            return True


    @cah.command()
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

    @cah.command()
    async def join(self, ctx, key: str):
        if key not in self.games:
            pass
        user = ctx.author
        if user.id in self.players:
            pass
        ref = self.games[key]
        game = ref['game']

        if game.add_player(Player(user.id, user.display_name)):
            self.players[user.id] = game.key
            await user.send(
                    "Thanks for joining Cards Against Humanity game {game.key} in {guild.name} {channel.mention}.\nIt will start shortly.".format(
                        game=game, guild=ref['guild'], channel=ref['channel']
                    )
                )
        else:
            pass

    @cah.command()
    async def start(self, ctx):
        user = ctx.author
        if user.id not in self.players:
            pass

        key = self.players[user.id]
        if key not in self.games:
            pass
        ref = self.games[key]
        game = ref['game']
        
        # The game requires you to be a member in order to start it
        if user.id not in game.players:
            await user.send(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because you haven't joined it.".format(
                    game=game, guild=ref['guild'], channel=ref['channel']
                )
            )
            return False
        # The game requires at least 3 players
        if len(game.players) < 3:
            await user.send(
                "You cannot start the Cards Against Humanity game {game.key} in {guild.name} {channel.mention} because it doesn't have enough players yet.".format(
                    game=game, guild=ref['guild'], channel=ref['channel']
                )
            )
            return False
        
        # Start the game!
        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Started by {user.display_name}!",
            color=0x00FFFF,
        )
        embed.set_footer(
            text="Cards Against Humanity game {game.key}".format(game=game)
        )
        await ref['channel'].send(embed=embed)
        return True

    @cah.command()
    async def submit(self, ctx, *args):
        user = ctx.author
        if user.id not in self.players:
            pass

        key = self.players[user.id]
        if key not in self.games:
            pass
        ref = self.games[key]
        game = ref['game']

        if user.id not in game.players:
            pass
        player = game.players[user.id]
        
        answer = []
        for i in args:
            j = int(i)
            a = player.hand[j - 1]
            answer.append(a)

        logger.info('Submit: {}'.format(answer))
        logger.info('Submit: {}'.format(game.question.fill_in(answer)))
        game.submit_answer(player, answer)
    
    @cah.command()
    async def debug(self, ctx):
        user = ctx.author
        if user.id not in self.players:
            pass

        key = self.players[user.id]
        if key not in self.games:
            pass
        ref = self.games[key]
        game = ref['game']

        game.start_round()
        for player_id in game.players:
            user = self.bot.get_user(player_id)
            hand = self._build_hand_embed(game, player_id)
            msg = await user.send(embed=hand)
