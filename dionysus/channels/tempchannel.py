import logging
import typing

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class TempChannel:
    COLOR = 0xFFFF00
    PREFIX = "♻"
    LOCKED = "🔒"
    UNLOCKED = "🔓"
    VISIBLE = "👀"
    HIDDEN = "👻"

    names: typing.Dict[str, "TempChannel"] = {}
    text_channels: typing.Dict[discord.TextChannel, "TempChannel"] = {}
    voice_channels: typing.Dict[discord.VoiceChannel, "TempChannel"] = {}

    @classmethod
    async def convert(cls, ctx: commands.Context, argument) -> "TempChannel":
        try:
            return cls.names[argument]
        except KeyError:
            raise commands.BadArgument(f"Could not convert {argument} to a TempChannel")

    @classmethod
    def by_name(cls, name: str) -> "TempChannel":
        return cls.names[name]

    @classmethod
    def by_text_channel(cls, text_channel: discord.TextChannel) -> "TempChannel":
        return cls.text_channels[text_channel]

    @classmethod
    def by_voice_channel(cls, voice_channel: discord.VoiceChannel) -> "TempChannel":
        return cls.voice_channels[voice_channel]

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
        self._visible = True
        self._limit = 10
        self._allows = []
        self._denys = []

        TempChannel.names[self.name] = self

    async def delete(self):
        TempChannel.names.pop(self.name)
        if self.text_channel:
            TempChannel.text_channels.pop(self.text_channel, None)
            await self.text_channel.delete()
        if self.voice_channel:
            TempChannel.voice_channels.pop(self.voice_channel, None)
            await self.voice_channel.delete()

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

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, state: bool):
        if state != self._visible:
            self._visible = state
            self.bot.loop.create_task(self._update_management_message())

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, value: int):
        if value != self._limit:
            self._limit = value
            self.bot.loop.create_task(self._update_management_message())

    async def setup(self, category: discord.CategoryChannel):
        logger.info(
            f"Setting up {self.name} in {'voice' if self.voice else 'text'} mode..."
        )
        self.text_channel = await category.create_text_channel(self.channel_name)
        TempChannel.text_channels[self.text_channel] = self
        if self.voice:
            self.voice_channel = await category.create_voice_channel(self.channel_name)
            TempChannel.voice_channels[self.voice_channel] = self

        await self._update_management_message()

    def restore(self):
        pass

    def _build_management_embed(self):
        description = (
            f"Owner: {self.owner.mention if self.owner else 'None'}\n"
            f"Status: {self.LOCKED if self._locked else self.UNLOCKED} {self.VISIBLE if self._visible else self.HIDDEN}"
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
