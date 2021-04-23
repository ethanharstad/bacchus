import logging
import os

import dice
import discord
from discord.ext import commands

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents(
    guilds=True,
    messages=True,
    reactions=True,
)
bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def ping(ctx):
    logging.info("got ping")
    await ctx.send("pong")


@bot.command()
async def roll(ctx, fmt: str = "1d6"):
    logging.info("Got dice command {fmt}")
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


bot.run(os.environ["DISCORD_TOKEN"])
