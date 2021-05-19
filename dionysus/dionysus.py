import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
)

import os
import random

import dice
import discord
from discord.ext import commands

from games.cah.cog import CardsAgainstHumanityCog

COMMAND_PREFIX = "?"

logger = logging.getLogger(__name__)

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    reactions=True,
)
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

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
    logger.info("We have logged in as {0.user}".format(bot))


@bot.event
async def on_reaction_add(reaction, user):
    logger.info(
        "on_reaction_add msg:{reaction.message.id} user:{user.id}".format(
            reaction=reaction, user=user
        )
    )
    # Ignore reactions by the bot
    if user.bot:
        return

    # Ignore messages we aren't tracking
    if reaction.message.id not in msg_refs:
        logger.info(
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
    logger.info("got ping")
    await ctx.send("pong")


@bot.command()
async def roll(ctx, fmt: str = "1d6"):
    logger.info("Got dice command {fmt}".format(fmt=fmt))
    try:
        roll = dice.roll(fmt)
    except dice.DiceBaseException as e:
        await ctx.send(e.pretty_print())
        logger.error("Dice Error", exc_info=e)
        return

    if len(roll) > 1:
        msg = "🎲 Rolled {roll} for total of {sum} 🎲".format(
            roll=", ".join(str(x) for x in roll), sum=sum(roll)
        )
    else:
        msg = "🎲 Rolled {roll} 🎲".format(roll=roll[0])

    await ctx.send(msg)


bot.add_cog(CardsAgainstHumanityCog(bot))

bot.run(os.environ["DISCORD_TOKEN"])
