import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class TempChannel:
    COLOR = 0xFFFF00
    PREFIX = "♻"
    LOCKED = "🔒"
    UNLOCKED = "🔓"

    def __init__(self, bot: commands.Bot, name: str, voice: bool = False):
        self.bot = bot
        tokens = name.split(" ")
        self.name = "-".join(tokens)
        self.voice = voice

        self.text_channel: discord.TextChannel = None
        self.voice_channel: discord.VoiceChannel = None
        self.management_message: discord.Message = None
        self._owner: discord.User = None
        self._locked = False

    @property
    def channel_name(self):
        return f"{self.PREFIX}-{self.name}"

    @property
    def owner(self) -> discord.User:
        return self._owner

    @owner.setter
    def owner(self, owner: discord.User):
        self._owner = owner
        self.bot.loop.create_task(self._update_management_message())

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, state: bool):
        if state != self._locked:
            self._locked = state
            self.bot.loop.create_task(self._update_management_message())

    async def setup(self, category: discord.CategoryChannel):
        logger.info(
            f"Setting up {self.name} in {'voice' if self.voice else 'text'} mode..."
        )
        self.text_channel = await category.create_text_channel(self.channel_name)
        if self.voice:
            self.voice_channel = await category.create_voice_channel(self.channel_name)

        await self._update_management_message()

    def restore(self):
        pass

    def _build_management_embed(self):
        description = (
            f"Owner: {self.owner.mention if self.owner else 'None'}\n"
            f"Status: {self.LOCKED if self._locked else self.UNLOCKED}"
        )
        embed = discord.Embed(
            color=self.COLOR,
            title=f"{self.name} Temporary Channel",
            description=description,
        )
        return embed

    async def _update_management_message(self):
        embed = self._build_management_embed()
        if self.management_message:
            await self.management_message.edit(embed=embed)
        else:
            self.management_message = await self.text_channel.send(embed=embed)

        if self.management_message.pinned == False:
            await self.management_message.pin()
