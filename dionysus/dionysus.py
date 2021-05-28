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

activity = discord.Game(
    name=emoji.emojize(":partying_face: Party Games :party_popper:")
)
intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    reactions=True,
)
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, activity=activity)

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
    if ctx.channel.type == discord.ChannelType.text:
        await ctx.message.delete()
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
    seed = random.randrange(100)
    i = random.randrange(len(GIFBALL_SEARCH_TERMS))
    search = GIFBALL_SEARCH_TERMS[i]
    question = _parse_question(args)
    try:
        response = giphy_api.gifs_search_get(giphy_key, search, limit=1, offset=seed)
        url = response.data[0].images.downsized_medium.url
        embed = discord.Embed(
            color=0xff0000,
            title="Magic Eight Ball",
            description=f"{ctx.author.display_name} asked: {question}\nThe 🎱 says..."
        )
        embed.set_thumbnail(url='http://d3s95l9oyr3kl.cloudfront.net/Magic_eight_ball.png')
        embed.set_image(url=url)
        if ctx.channel.type == discord.ChannelType.text:
            await ctx.message.delete()
        await ctx.send(embed=embed)
    except:
        logger.exception("OOPS")
        await ctx.send(f"Fuck you {ctx.author.display_name}, Leave me alone. I'm broken...")

bot.add_cog(CardsAgainstHumanityCog(bot))
bot.add_cog(RideTheBusCog(bot))

# RELEASE THE KRAKEN
bot.run(os.environ["DISCORD_TOKEN"])
