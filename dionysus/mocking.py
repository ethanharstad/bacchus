import logging
import random

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

random.seed()


class MockingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            # See if the bot was mentioned
            if self.bot.user.mentioned_in(message):
                if "fuck" in message.content.lower():
                    await message.reply(f"Well fuck you then {message.author.mention}!")
            else:
                await self._random_taunt(message)

    async def _random_taunt(self, message: discord.Message):
        if random.randrange(100) != 0:
            return
        logger.info(f"Being a dick to {message.author.name}...")
        f = random.choice([self._spongebobify])
        await f(message)

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
