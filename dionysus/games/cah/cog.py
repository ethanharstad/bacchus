import logging
import random
import discord
from discord.ext import commands

from .game import CardsAgainstHumanity, Player, ANSWERS, QUESTIONS

logging.basicConfig(level=logging.DEBUG)

CAH_GAMES = {}


class CardsAgainstHumanityCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def cah_build_hand_embed(self, game: CardsAgainstHumanity, player_id: int):
        player: Player = game.players[player_id]

        embed = discord.Embed(
            title="Cards Against Humanity",
            description="Choose your best answer to:\n{}".format(game.question),
            color=0x00FFFF,
        )

        for i, answer in player.hand:
            embed.add_field(name="{}".format(i + 1), value=str(answer), inline=False)

        return embed


    def cah_build_judge_embed(self, game: CardsAgainstHumanity):
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
            CAH_GAMES[game.key] = game

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
            embed.add_field(name="👍", value="to join", inline=True)
            embed.add_field(name="✅", value="to start", inline=True)

            msg = await ctx.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("✅")

            msg_refs[msg.id] = {
                "msg": msg,
                "callback": cah_prestart,
                "ctx": ctx,
                "game": game.key,
            }

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


    async def cah_prestart(self, reaction: discord.Reaction, user: discord.User, **kwargs):
        # Lookup the game
        game_key = kwargs["game"]
        if game_key not in CAH_GAMES:
            return False
        game = CAH_GAMES[game_key]

        # Debugging tools
        if reaction.emoji == "🃏":
            question = game.start_round()
            for player_id in game.players:
                player = game.players[player_id]
                user = self.bot.get_user(player_id)
                hand = discord.Embed(
                    title="Cards Against Humanity",
                    description="React to select the best answer(s) for:\n> {}".format(
                        question
                    ),
                    color=0x00FFFF,
                )
                for index, card in enumerate(player.hand):
                    hand.add_field(
                        name=NUMERIC_REACTIONS[index], value=str(card), inline=False
                    )
                hand.add_field(name="❌", value="Leave the game", inline=False)
                msg = await user.send(embed=hand)
                for i in range(len(player.hand)):
                    await msg.add_reaction(emoji=NUMERIC_REACTIONS[i])
                await msg.add_reaction(emoji="❌")
            return False

        # Try to join the game
        if reaction.emoji == "👍":
            if game.add_player(Player(user.id, user.display_name)):
                await user.send(
                    "Thanks for joining Cards Against Humanity game {game.key} in {reaction.message.guild.name} {reaction.message.channel.mention}.\nIt will start shortly.".format(
                        game=game, reaction=reaction
                    )
                )
            else:
                # TODO should probably tell the user something here
                await reaction.remove(user)
            return False

        # Try to start the game
        if reaction.emoji == "✅":
            # The game requires you to be a member in order to start it
            if user.id not in game.players:
                await user.send(
                    "You cannot start the Cards Against Humanity game {game.key} in {reaction.message.guild.name} {reaction.message.channel.mention} because you haven't joined it.".format(
                        game=game, reaction=reaction
                    )
                )
                await reaction.remove(user)
                return False
            # The game requires at least 3 players
            if len(game.players) < 3:
                await user.send(
                    "You cannot start the Cards Against Humanity game {game.key} in {reaction.message.guild.name} {reaction.message.channel.mention} because it doesn't have enough players yet.".format(
                        game=game, reaction=reaction
                    )
                )
                await reaction.remove(user)
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
            await reaction.message.channel.send(embed=embed)
            return True
