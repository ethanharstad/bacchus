import logging
import os

import dice
import discord
from discord.ext import commands

from games.cah.game import CardsAgainstHumanity, Player

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    reactions=True,
)
bot = commands.Bot(command_prefix="?", intents=intents)

# Messages we are tracking for responses
msg_refs = {}

NUMERIC_REACTIONS = [
    "1\N{COMBINING ENCLOSING KEYCAP}",
    "2\N{COMBINING ENCLOSING KEYCAP}",
    "3\N{COMBINING ENCLOSING KEYCAP}",
    "4\N{COMBINING ENCLOSING KEYCAP}",
    "5\N{COMBINING ENCLOSING KEYCAP}",
    "6\N{COMBINING ENCLOSING KEYCAP}",
    "7\N{COMBINING ENCLOSING KEYCAP}",
    "8\N{COMBINING ENCLOSING KEYCAP}",
    "9\N{COMBINING ENCLOSING KEYCAP}",
    "0\N{COMBINING ENCLOSING KEYCAP}",
]


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.event
async def on_reaction_add(reaction, user):
    logging.info(
        "on_reaction_add msg:{reaction.message.id} user:{user.id}".format(
            reaction=reaction, user=user
        )
    )
    # Ignore reactions by the bot
    if user.bot:
        return

    # Ignore messages we aren't tracking
    if reaction.message.id not in msg_refs:
        logging.info(
            "Could not process reaction to msg id {}".format(reaction.message.id)
        )
        return

    # Attempt to handle the reaction
    val = await msg_refs[reaction.message.id]["callback"](
        reaction, user, **msg_refs[reaction.message.id]
    )
    if val:
        msg_refs.pop(reaction.message.id)


@bot.command()
async def ping(ctx):
    logging.info("got ping")
    await ctx.send("pong")


@bot.command()
async def roll(ctx, fmt: str = "1d6"):
    logging.info("Got dice command {fmt}".format(fmt=fmt))
    try:
        roll = dice.roll(fmt)
    except dice.DiceBaseException as e:
        await ctx.send(e.pretty_print())
        logging.error("Dice Error", exc_info=e)
        return

    if len(roll) > 1:
        msg = "🎲 Rolled {roll} for total of {sum} 🎲".format(
            roll=", ".join(str(x) for x in roll), sum=sum(roll)
        )
    else:
        msg = "🎲 Rolled {roll} 🎲".format(roll=roll[0])

    await ctx.send(msg)


@bot.group()
async def games(ctx):
    if ctx.invoked_subcommand is None:
        # Build base embed
        embed = discord.Embed(
            title="Games",
            description="React or use ?games {{KEY}} to start a game",
            color=0x00FFFF,
        )
        embed.set_footer(
            text="Information requested by {}".format(ctx.author.display_name)
        )

        # Build game fields
        for g in games_fields:
            embed.add_field(
                name="{emoji} {name} {{{slug}}}".format(**g),
                value="{description}".format(**g),
                inline=False,
            )

        # Send message
        msg = await ctx.send(embed=embed)
        msg_refs[msg.id] = {
            "msg": msg,
            "callback": on_games_reaction,
            "ctx": ctx,
        }

        # Add reactions
        for g in games_fields:
            await msg.add_reaction(g["emoji"])


async def on_games_reaction(reaction: discord.Reaction, user: discord.User, **kwargs):
    logging.info("Handling reaction")
    try:
        game = next(g for g in games_fields if g["emoji"] == reaction.emoji)
        return await game["callback"](kwargs["ctx"])
    except StopIteration:
        logging.info(
            "Emojii {reaction.emoji} is not mapped to a game!".format(reaction=reaction)
        )


CAH_GAMES = {}


@games.command()
async def cah(ctx, user: discord.User = None):
    user = user or ctx.author
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


async def cah_prestart(reaction: discord.Reaction, user: discord.User, **kwargs):
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
            user = bot.get_user(player_id)
            hand = discord.Embed(
                title="Cards Against Humanity",
                description="React to selection the best answer(s) for:\n> {}".format(
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


games_fields = [
    {
        "emoji": "🙊",
        "slug": "cah",
        "name": "Cards Against Humanity",
        "description": "Fill in the blank using politically incorrect words or phrases.",
        "callback": cah,
    },
]


bot.run(os.environ["DISCORD_TOKEN"])
