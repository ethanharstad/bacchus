import logging
from typing import Dict, Union, Optional

import discord
from discord.ext import commands

from .tempchannel import TempChannel

logger = logging.getLogger(__name__)

COLOR = 0xFFFF00


class ChannelsCog(commands.Cog, name="Channels"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot

    @commands.group(brief="Temporary Channel Management")
    async def channels(self, ctx: commands.Context) -> None:
        # Don't respond to bots
        if ctx.author.bot:
            return
        # Don't respond if the user mean a subcommand
        if ctx.invoked_subcommand is not None:
            return

        embed = discord.Embed(
            color=COLOR,
            title="Temporary Channels",
            description="Manage temporary channels.",
        )
        await ctx.send(embed=embed)

    @channels.command()
    async def create(self, ctx: commands.Context, type: str, name: str) -> None:
        category = discord.utils.get(ctx.guild.channels, name="temp-channels")
        channel = TempChannel(self.bot, name=name, voice=type.lower() == "voice")
        await channel.setup(category)
        channel.owner = ctx.author

    @create.error
    async def create_error(self, ctx: commands.Context, error: commands.CommandError):
        logger.error(error)
        await ctx.send_help(ctx.command)

    @channels.command()
    async def delete(
        self, ctx: commands.Context, channel: Optional[TempChannel]
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)

        await channel.delete()

    @channels.command()
    async def claim(
        self, ctx: commands.Context, channel: Optional[TempChannel]
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        channel.owner = ctx.author

    @channels.command()
    async def lock(self, ctx: commands.Context, channel: Optional[TempChannel]) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.locked = True

    @channels.command()
    async def unlock(
        self, ctx: commands.Context, channel: Optional[TempChannel]
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.locked = False

    @channels.command()
    async def ghost(
        self, ctx: commands.Context, channel: Optional[TempChannel]
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.visible = False

    @channels.command()
    async def unghost(
        self, ctx: commands.Context, channel: Optional[TempChannel]
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.visible = True

    @channels.command()
    async def allow(
        self,
        ctx: commands.Context,
        channel: Optional[TempChannel],
        who: Union[discord.User, discord.Role],
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        channel.allow(who)

    @channels.command()
    async def deny(
        self,
        ctx: commands.Context,
        channel: Optional[TempChannel],
        who: discord.User,
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        channel.deny(who)

    @channels.command()
    async def limit(
        self, ctx: commands.Context, channel: Optional[TempChannel], limit: int
    ) -> None:
        if channel is None:
            channel = TempChannel.by_text_channel(ctx.channel)
        channel.limit = limit

    @channels.command()
    async def invite(
        self, ctx: commands.Context, channel: Optional[TempChannel], who: discord.User
    ) -> None:
        pass

    # @channels.command()
    # async def archive(self, ctx: commands.Context, name: Optional[str]) -> None:
    #     pass

    # @channels.command()
    # async def unarchive(self, ctx: commands.Context, name: Optional[str]) -> None:
    #     pass

    def _is_owner(self, ctx: commands.Context, channel: TempChannel) -> bool:
        return ctx.author == channel.owner

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.bot.guilds:
            category = discord.utils.get(guild.channels, name="temp-channels")
            if not category:
                continue
            for channel in category.channels:
                c = str(channel.name[0])
                logger.info(f"Checking {channel.name} {type(c)} {c} {len(c)}...")
                if c == TempChannel.PREFIX:
                    logger.info(f"Deleting {channel.name}...")
                    await channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        logger.info(f"User: {member.name}\nBefore: {before}\nAfter: {after}")
        # Is this user in a channel
        if after.channel is None:
            return
        channel = TempChannel.by_voice_channel(after.channel)
        if channel is None:
            return
        # Has the channel changed
        if after.channel is not before.channel:
            if not channel.validate_user(member):
                await member.move_to(None, reason="Not authorized to join this channel")
