import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
)

import random
import os

import dice
import discord
from discord.ext import commands
import emoji
import giphy_client

from games.cah.cog import CardsAgainstHumanityCog
from games.ridethebus.cog import RideTheBusCog

COMMAND_PREFIX = "?"

logger = logging.getLogger(__name__)

random.seed()

# Setup giphy
giphy_api = giphy_client.DefaultApi()
giphy_key = os.environ['GIPHY_API_KEY']

# Set discord status
activity = discord.Game(
    name=emoji.emojize(":partying_face: Party Games :party_popper:")
)
# Set discord permissions
intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    reactions=True,
)
# Configure discord bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, activity=activity)


@bot.event
async def on_ready():
    logger.info("We have logged in as {0.user}".format(bot))
    
@bot.event
async def on_message(message):
    # See if the bot was mentioned
    if bot.user.mentioned_in(message):
        if 'fuck' in message.content:
            await message.reply("Fuck you too!")
    # See if any commands were in this message
    await bot.process_commands(message)


@bot.command()
async def ping(ctx: commands.Context):
    logger.info("got ping")
    await ctx.send("pong")


@bot.command()
async def roll(ctx: commands.Context, fmt: str = "1d6"):
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
    
EIGHT_BALL_RESPONSES = [
    "Yes definetely.",
    "Most likely.",
    "Ask again later.",
    "Don't count on it.",
    "Yes, but do it drunk as fuck 🍺", 
    "No Chance",
    "You can't handle the truth",
    "whatever",
    "Maybe, if you leave me alone",
    "8===D",
    "8===D~~",
    "you've got to be kitten.... 🐱",
    "Dear god NO",
    "lol the fuck you think?",
    "Pervert."
]

def _parse_question(words):
    if len(words) > 0:
        question = ' '.join(words)
        question = question if question[-1] == '?' else question + '?'
    else:
        question = "Nothing like a noob!"
    return question

async def _delete_message(msg: discord.Message):
    # If this isn't a private message, delete the original message
    if msg.channel.type == discord.ChannelType.text:
        await msg.delete()

# Define a new command on the bot
# This is a decorator, probably a ways from actually learning these, for now know it's copied from the discord library documentation
@bot.command(name="8ball")
# Make our own function, "async" is new and might not be in your course
async def eight_ball(ctx: commands.Context, *args):
    # Get the length of the possible responses
    n = len(EIGHT_BALL_RESPONSES)
    # Get a random integer in the range of the number of possible responses
    i = random.randrange(n)
    # Use the random integer to get the response
    response = EIGHT_BALL_RESPONSES[i]
    # Reformat the question
    question = _parse_question(args)
    # Try to delete the message
    await _delete_message(ctx.message)
    # Build the embed
    embed = discord.Embed(
        color=0xff0000,
        title="Magic Eight Ball",
        description=f"{ctx.author.display_name} asked: {question}\nThe 🎱 says **{response}**"
    )
    embed.set_thumbnail(url='http://d3s95l9oyr3kl.cloudfront.net/Magic_eight_ball.png')
    await ctx.send(embed=embed)


GIFBALL_SEARCH_TERMS = [
    "fuck yes",
    "fuck no",
    "hell yes",
    "hell no",
    "shutup",
    "who are you",
    "dont be a dick",
]

@bot.command()
async def gifball(ctx: commands.Context, *args):
    # Pick a random offset to get a random gif
    seed = random.randrange(100)
    # Pick a search term at random
    i = random.randrange(len(GIFBALL_SEARCH_TERMS))
    search = GIFBALL_SEARCH_TERMS[i]
    # Format the question that they asked
    question = _parse_question(args)
    try:
        # Search giphy
        response = giphy_api.gifs_search_get(giphy_key, search, limit=1, offset=seed)
        # Extract the URL for an image
        url = response.data[0].images.downsized_medium.url
        # Build the embed
        embed = discord.Embed(
            color=0xff0000,
            title="Magic Eight Ball",
            description=f"{ctx.author.display_name} asked: {question}\nThe 🎱 says..."
        )
        embed.set_thumbnail(url='http://d3s95l9oyr3kl.cloudfront.net/Magic_eight_ball.png')
        embed.set_image(url=url)
        # Try to delete the message I LOVE YOU!!!!!!!!!!!!!!!<-------
        await _delete_message(ctx.message)
        # Send the response
        await ctx.send(embed=embed)
    except:
        # Something went wrong
        logger.exception("OOPS")
        await ctx.send(f"Fuck you {ctx.author.display_name}, Leave me alone. I'm broken...")

bot.add_cog(CardsAgainstHumanityCog(bot))
bot.add_cog(RideTheBusCog(bot))

# RELEASE THE KRAKEN
bot.run(os.environ["DISCORD_TOKEN"])
