import logging
import random
import re

from better_profanity import profanity
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

random.seed()

profanity.load_censor_words()

HI_DAD_PATTERN = re.compile(r"^i'?m\s", re.IGNORECASE)


class MockingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Don't bother replying to bots
        if not message.author.bot:
            # Get the context so we can see if it contains a command
            ctx: discord.commands.Context = await self.bot.get_context(message)
            # Only be a dick if there are no commands
            if ctx.valid is False:
                # If any dickery happens, immediately return
                # TODO solve this more elegantly
                if await self._profanity(message):
                    return
                if await self._hi_dad(message):
                    return
                if await self._random_taunt(message):
                    return
                # If we weren't a dick, maybe they need help?
                await self._needs_help(message)

    async def _needs_help(self, message: discord.Message):
        if self.bot.user.mentioned_in(message):
            await message.reply(
                f"¯\_(ツ)_/¯ perhaps you want `{self.bot.command_prefix}help`?"
            )

    async def _profanity(self, message: discord.Message) -> bool:
        if profanity.contains_profanity(message.content):
            if random.randrange(5) == 0:
                # TODO add more responses to profanity filter
                reply = random.choice(
                    [
                        "Dirty, dirty boy!",
                        "Oh my stars...",
                        "That's a naughty word!",
                        "I'm telling Mom you said that!",
                        "You got a dirty mouth.",
                    ]
                )
                await message.reply(reply)
                return True
        return False

    async def _hi_dad(self, message: discord.Message) -> bool:
        if HI_DAD_PATTERN.match(message.content):
            tokens = message.content.split(" ")
            await message.reply(f"Hi {tokens[1]}, I'm Dad.")
            return True
        return False

    async def _random_taunt(self, message: discord.Message) -> bool:
        if random.randrange(100) != 0:
            return False
        logger.info(f"Being a dick to {message.author.name}...")
        f = random.choice([self._spongebobify])
        await f(message)
        return True

    async def _spongebobify(self, message: discord.Message):
        content: str = message.content.lower()
        ret = ""
        i = True  # capitalize
        for char in content:
            if i:
                ret += char.upper()
            else:
                ret += char.lower()
            if char != " ":
                i = not i
        await message.reply(ret)
