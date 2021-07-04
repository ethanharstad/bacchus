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
    async def cleanup(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        # logger.info(f"{type(PREFIX)} {PREFIX} {len(PREFIX)}")
        # for channel in guild.channels:
        #     c = str(channel.name[0])
        #     logger.info(f"Checking {channel.name} {type(c)} {c} {len(c)}...")
        #     if c == PREFIX:
        #         logger.info(f"Deleting {channel.name}...")
        #         await channel.delete()

    @channels.command()
    async def create(self, ctx: commands.Context, type: str, name: str) -> None:
        category = discord.utils.get(ctx.guild.channels, name="temp-channels")
        channel = TempChannel(self.bot, name=name, voice=type.lower() == "voice")
        await channel.setup(category)

    @create.error
    async def create_error(self, ctx: commands.Context, error: commands.CommandError):
        logger.error(error)
        await ctx.send_help(ctx.command)

    @channels.command()
    async def delete(self, ctx: commands.Context, name: str = None) -> None:
        channel = await self._get_channel(ctx, name)
        if channel is None:
            return

        await channel.delete()

    @channels.command()
    async def claim(self, ctx: commands.Context, name: str = None) -> None:
        channel = await self._get_channel(ctx, name)
        if channel is None:
            return
        channel.owner = ctx.author

    @channels.command()
    async def lock(self, ctx: commands.Context, name: str = None) -> None:
        channel = await self._get_channel(ctx, name)
        if channel is None:
            return
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.locked = True

    @channels.command()
    async def unlock(self, ctx: commands.Context, name: str = None) -> None:
        channel = await self._get_channel(ctx, name)
        if channel is None:
            return
        if not self._is_owner(ctx, channel):
            await ctx.reply("Sorry, you need to be the channel owner.")
            return
        channel.locked = False

    @channels.command()
    async def allow(
        self, ctx: commands.Context, who: Union[discord.Role, discord.User]
    ) -> None:
        if isinstance(who, discord.Role):
            t = "Role"
        elif isinstance(who, discord.User):
            t = "User"
        await ctx.reply(f"Allowing {t} {who.mention}")

    @channels.command()
    async def deny(
        self, ctx: commands.Context, who: Union[discord.Role, discord.User]
    ) -> None:
        pass

    @channels.command()
    async def limit(
        self, ctx: commands.Context, channel: Optional[TempChannel], limit: int
    ) -> None:
        logger.info(f"Got limit command for {channel.name}")

    @channels.command()
    async def archive(self, ctx: commands.Context, name: Optional[str]) -> None:
        pass

    @channels.command()
    async def unarchive(self, ctx: commands.Context, name: Optional[str]) -> None:
        pass

    async def _get_channel(self, ctx: commands.Context, name: str) -> TempChannel:
        channel = None
        try:
            if name is not None:
                channel = TempChannel.by_name(name)
            else:
                channel = TempChannel.by_text_channel(ctx.channel)
        except:
            if name is not None:
                await ctx.reply(f"Could not find a channel named {name}.")
            else:
                await ctx.reply(
                    "Please pass a channel name or run the command from the channel you want to close."
                )
        return channel

    def _is_owner(self, ctx: commands.Context, channel: TempChannel) -> bool:
        return ctx.author == channel.owner
