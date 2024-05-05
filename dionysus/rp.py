import logging
import random

logger = logging.getLogger(__name__)

random.seed()

import discord
from discord.ext import commands

class RoleplayCog(commands.Cog, name="Roleplay"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot: commands.Bot = bot
    
    @commands.group()
    async def rp(self, ctx: commands.Context) -> None:
        pass

    @rp.command()
    async def tackle(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got tackle command {target}".format(target=target))
        embed = discord.Embed(
            title='Tackled!',
            description=f"{ctx.author.mention} tackled {target.mention}!"
        )
        url = random.choice([
            'https://i.giphy.com/3ohze0w4rqZtqt08PS.gif',
            'https://i.giphy.com/jULCKZmMGlZ7DPZbQr.gif',
            'https://c.tenor.com/JM6lOcNo7gkAAAAC/tenor.gif',
            'https://c.tenor.com/vwy_WZsXfwUAAAAd/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)
