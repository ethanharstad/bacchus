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
        return cls.names.get(name, None)

    @classmethod
    def by_text_channel(cls, text_channel: discord.TextChannel) -> "TempChannel":
        return cls.text_channels.get(text_channel, None)

    @classmethod
    def by_voice_channel(cls, voice_channel: discord.VoiceChannel) -> "TempChannel":
        return cls.voice_channels.get(voice_channel, None)

    def __init__(self, bot: commands.Bot, name: str, voice: bool = False):
        self.bot = bot
        tokens = name.split(" ")
        self.name = "-".join(tokens)
        self.voice = voice

        self.guild: discord.Guild = None
        self.role: discord.Role = None
        self.text_channel: discord.TextChannel = None
        self.voice_channel: discord.VoiceChannel = None
        self.management_message: discord.Message = None
        self._owner: discord.User = None
        self._locked = False
        self._visible = True
        self._limit = 10
        self._allowed_users: typing.Set[discord.User] = set()
        self._allowed_roles: typing.Set[discord.Role] = set()
        self._denys: typing.Set[discord.User] = set()

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
        if value < 0:
            raise ValueError("Limit must be greater than or equal to 0")
        if value != self._limit:
            self._limit = value
            self.bot.loop.create_task(self._update_management_message())

    async def setup(self, category: discord.CategoryChannel):
        logger.info(
            f"Setting up {self.name} in {'voice' if self.voice else 'text'} mode..."
        )
        self.guild = category.guild
        self.text_channel = await category.create_text_channel(self.channel_name)
        TempChannel.text_channels[self.text_channel] = self
        if self.voice:
            self.voice_channel = await category.create_voice_channel(self.channel_name)
            TempChannel.voice_channels[self.voice_channel] = self

        await self._update_management_message()

    def restore(self):
        pass

    def allow(self, target: typing.Union[discord.User, discord.Role]):
        if isinstance(target, discord.Role):
            t = "Role"
            allows = self._allowed_roles
        elif isinstance(target, discord.User):
            t = "User"
            self._denys.discard(target)
            allows = self._allowed_users
        else:
            return
        if target not in allows:
            logger.info(f"Allowing {t} {target} in {self.name}")
            allows.add(target)
            self.bot.loop.create_task(self._update_management_message())

    def deny(self, target: discord.User):
        if target not in self._denys:
            logger.info(f"Denying User {target} in {self.name}")
            self._denys.add(target)
            self._allowed_users.discard(target)
            self.bot.loop.create_task(self._update_management_message())

    def validate_user(self, user: discord.User) -> bool:
        logger.info(f"Trying to validate {user.name} for {self.name}")
        if self._locked == False:
            logger.info(f"Allowing {user.name} because the channel is unlocked")
            return True
        if self._owner == user:
            logger.info(f"Allowing {user.name} because they are the channel owner")
            return True
        if user in self._denys:
            return False
        if user in self._allowed_users:
            return True
        member = self.guild.get_member(user.id)
        if set(member.roles).isdisjoint(self._allowed_roles) == False:
            return True

        return False

    def _build_management_embed(self):
        description = (
            f"Owner: {self.owner.mention if self.owner else 'None'}\n"
            f"Status: {self.LOCKED if self._locked else self.UNLOCKED} {self.VISIBLE if self._visible else self.HIDDEN}\n"
            f"Limit: {self._limit if self._limit > 0 else 'Unlimited'}\n"
            "Allowed:\n"
            f"{chr(10).join(map(lambda x: x.mention,self._allowed_roles))}"
            f"{chr(10) if len(self._allowed_roles) > 0 else None}"
            f"{chr(10).join(map(lambda x: x.mention,self._allowed_users))}"
            f"{chr(10) if len(self._allowed_users) > 0 else None}"
            "Denied:\n"
            f"{chr(10).join(map(lambda x: x.mention,self._denys))}"
        )
        embed = discord.Embed(
            color=self.COLOR,
            title=f"{self.name} Temporary Channel",
            description=description,
        )
        return embed

    async def _update_management_message(self):
        if self.text_channel:
            embed = self._build_management_embed()
            if self.management_message:
                await self.management_message.edit(embed=embed)
            else:
                self.management_message = await self.text_channel.send(embed=embed)

            if self.management_message.pinned == False:
                await self.management_message.pin()
