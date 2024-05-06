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

    @rp.command()
    async def hug(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got hug command {target}".format(target=target))
        embed = discord.Embed(
            title='Hugged!',
            description=f"{ctx.author.mention} hugged {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/1gf_Jz8WYH0AAAAC/tenor.gif',
            'https://c.tenor.com/JKo6Z5x3slYAAAAC/tenor.gif',
            'https://c.tenor.com/wUseBC_w3xQAAAAd/tenor.gif',
            'https://c.tenor.com/rEszkHLiEMUAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    
    @rp.command()
    async def pounce(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got pounce command {target}".format(target=target))
        embed = discord.Embed(
            title='Pounced!',
            description=f"{ctx.author.mention} pounced on {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/xx6asPvcQ3gAAAAC/tenor.gif',
            'https://c.tenor.com/lrQo49ZewMAAAAAC/tenor.gif',
            'https://c.tenor.com/C2mPihbW61MAAAAC/tenor.gif',
            'https://c.tenor.com/NADxobrBrxYAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    
    @rp.command()
    async def kidnap(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got kidnap command {target}".format(target=target))
        embed = discord.Embed(
            title='Kidnapped!',
            description=f"{ctx.author.mention} kidnapped {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/VqDyy5WnMWkAAAAC/tenor.gif',
            'https://c.tenor.com/K5hSi-76ZXIAAAAC/tenor.gif',
            'https://c.tenor.com/ONYRw7p9j-gAAAAC/tenor.gif',
            'https://c.tenor.com/lhKSYOk8KTEAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def bite(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got bit command {target}".format(target=target))
        embed = discord.Embed(
            title='Bitten!',
            description=f"{ctx.author.mention} bites {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/hMQJfgJfvW4AAAAC/tenor.gif',
            'https://c.tenor.com/oQ4xyPruQQEAAAAC/tenor.gif',
            'https://c.tenor.com/6mJKmDho1b4AAAAC/tenor.gif',
            'https://c.tenor.com/q34DEzUWsVUAAAAC/tenor.gif',
            'https://c.tenor.com/nrZhF1f6JY4AAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def pindown(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got pindown command {target}".format(target=target))
        embed = discord.Embed(
            title='Pinned!',
            description=f"{ctx.author.mention} pins {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/vvuqAk8n4DYAAAAC/tenor.gif',
            'https://c.tenor.com/GHg2M_XvSQoAAAAC/tenor.gif',
            'https://c.tenor.com/-ozRM-R0vCQAAAAd/tenor.gif',
            'https://c.tenor.com/5xD_EmMx_38AAAAC/tenor.gif',
            'https://c.tenor.com/s9F1taEGFeAAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def siton(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got siton command {target}".format(target=target))
        embed = discord.Embed(
            title='Sat On!',
            description=f"{ctx.author.mention} sits on {target.mention}!"
        )
        url = random.choice([
            'https://media.tenor.com/qm9AgcDKIkMAAAAi/jump.gif',
            'https://c.tenor.com/mXiU-3yw8yUAAAAC/tenor.gif',
            'https://c.tenor.com/xJ4_OAaR8E8AAAAd/tenor.gif',
            'https://c.tenor.com/75LEGockvpEAAAAd/tenor.gif',   
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def cuddle(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got cuddle command {target}".format(target=target))
        embed = discord.Embed(
            title='Cuddles!',
            description=f"{ctx.author.mention} cuddles {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/NAACz7Er2lsAAAAC/tenor.gif',
            'https://c.tenor.com/GTlDCm4P4EsAAAAC/tenor.gif',
            'https://c.tenor.com/eRSiBtkX5zwAAAAC/tenor.gif',
            'https://c.tenor.com/Glql1LPSciQAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def punch(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got punch command {target}".format(target=target))
        embed = discord.Embed(
            title='Punched!',
            description=f"{ctx.author.mention} punches {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/RiLHXlSdFd4AAAAC/tenor.gif',
            'https://c.tenor.com/szPtb6lqakIAAAAC/tenor.gif',
            'https://c.tenor.com/jwGSFHGRyFUAAAAC/tenor.gif',
            'https://c.tenor.com/_qK7pH2wBoIAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def shinkick(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got shinkick command {target}".format(target=target))
        embed = discord.Embed(
            title='Kicked!',
            description=f"{ctx.author.mention} kicks {target.mention}'s shin!"
        )
        url = random.choice([
            'https://c.tenor.com/SOVjCFja6tMAAAAd/tenor.gif',
            'https://c.tenor.com/Erj44CRTRo0AAAAC/tenor.gif',
            'https://c.tenor.com/5yd_BtUNcE0AAAAC/tenor.gif',
            'https://c.tenor.com/ePmkhhm9aoUAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def lick(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got lick command {target}".format(target=target))
        embed = discord.Embed(
            title='Licked!',
            description=f"{ctx.author.mention} licks {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/citW1vt3UP4AAAAC/tenor.gif',
            'https://c.tenor.com/xTHywKIPrHgAAAAC/tenor.gif',
            'https://c.tenor.com/xzmRBPIaBsEAAAAC/tenor.gif',
            'https://c.tenor.com/OliXfzaOAfEAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def tongue(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got tongue command {target}".format(target=target))
        embed = discord.Embed(
            title='Sticks tongue out!',
            description=f"{ctx.author.mention} sticks tongue out at {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/dyhAMzK8RIkAAAAC/tenor.gif',
            'https://c.tenor.com/kvlwlKPAogMAAAAC/tenor.gif',
            'https://c.tenor.com/oSvH9D184qIAAAAC/tenor.gif',
            'https://c.tenor.com/7FU6U1xu0Q4AAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def poke(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got poke command {target}".format(target=target))
        embed = discord.Embed(
            title='Poked!',
            description=f"{ctx.author.mention} pokes {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/_C06NtBa8pcAAAAC/tenor.gif',
            'https://c.tenor.com/maGAJ074LXgAAAAC/tenor.gif',
            'https://c.tenor.com/9bPsSkaKgVsAAAAC/tenor.gif',
            'https://c.tenor.com/bY-gaxOFIj0AAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def nuzzle(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got nuzzle command {target}".format(target=target))
        embed = discord.Embed(
            title='Nuzzled!',
            description=f"{ctx.author.mention} nuzzles {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/Uz1dXTjjnkwAAAAC/tenor.gif',
            'https://c.tenor.com/bKBuTJqDu7cAAAAC/tenor.gif',
            'https://media.tenor.com/RQEWTNJC__YAAAAM/milk-and-mocha-love.gif',
            'https://media.tenor.com/eSk_xYNiHnUAAAAM/wolf-puppy.gif',
            'https://media.tenor.com/f-X7zsHaKOAAAAAM/sankarea-anime-nuzzle.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def plop(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got plop command {target}".format(target=target))
        embed = discord.Embed(
            title='Plops!',
            description=f"{ctx.author.mention} plops on {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/r48KFRbLZCgAAAAC/tenor.gif',
            'https://c.tenor.com/2oc9YvzCtXUAAAAC/tenor.gif',
            'https://c.tenor.com/BIAcdMYBCPYAAAAC/tenor.gif',
            'https://c.tenor.com/tmSq__XZFTwAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def slap(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got slap command {target}".format(target=target))
        embed = discord.Embed(
            title='Slap!',
            description=f"{ctx.author.mention} slaps {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/WsKM5ZDigvgAAAAC/tenor.gif',
            'https://c.tenor.com/smDvEFaac-cAAAAC/tenor.gif',
            'https://c.tenor.com/tfu-SnLkaP4AAAAC/tenor.gif',
            'https://c.tenor.com/u5laMosKAmgAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def steal(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got steal command {target}".format(target=target))
        embed = discord.Embed(
            title='Steals!',
            description=f"{ctx.author.mention} steals from {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/_jHMKINZLOUAAAAC/tenor.gif',
            'https://c.tenor.com/aLr2Y8Ajx_cAAAAC/tenor.gif',
            'https://c.tenor.com/E-yE8jUGMmQAAAAC/tenor.gif',
            'https://c.tenor.com/NH7haQy5XjkAAAAC/tenor.gif',
            'https://c.tenor.com/sO2uHuBmQfkAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def terrorize(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got terrorize command {target}".format(target=target))
        embed = discord.Embed(
            title='Terroize!',
            description=f"{ctx.author.mention} terrorizes {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/uUJjPnn47OwAAAAC/tenor.gif',
            'https://c.tenor.com/DQ5LKNih9u4AAAAC/tenor.gif',
            'https://c.tenor.com/QCWto5N6k0EAAAAC/tenor.gif',
            'https://c.tenor.com/GzYlN2cspHQAAAAC/tenor.gif',
            'https://c.tenor.com/CBndCdibmwUAAAAC/tenor.gif',
            'https://media.tenor.com/QRKXmc5qWpoAAAAi/mimibubu.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def smother(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got smother command {target}".format(target=target))
        embed = discord.Embed(
            title='Smothered!',
            description=f"{ctx.author.mention} smothers {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/jGEjxF0YPSwAAAAC/tenor.gif',
            'https://c.tenor.com/kDcIN19F1V0AAAAC/tenor.gif',
            'https://c.tenor.com/nzZCLW20Wb8AAAAC/tenor.gif',
            'https://c.tenor.com/k0W88frLulAAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def pout(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got pout command {target}".format(target=target))
        embed = discord.Embed(
            title='Pouts!',
            description=f"{ctx.author.mention} pouts at {target.mention}!"
        )
        url = random.choice([
            'https://media.tenor.com/FJYXjsubH58AAAAM/kitty-kitten.gif',
            'https://media.tenor.com/TDoaU1-fcDgAAAAM/pout-girl.gif',
            'https://c.tenor.com/uSejuv_JZgwAAAAC/tenor.gif',
            'https://c.tenor.com/N8H8B1_Zp6YAAAAC/tenor.gif',
            'https://c.tenor.com/9C9gUmUZh0sAAAAC/tenor.gif',
            'https://media.tenor.com/kjqof9l6gk8AAAAM/pikachu-sad.gif',
            'https://media.tenor.com/_3-IPPb314oAAAAM/agnes-despicable-me.gif',
            'https://c.tenor.com/mwQV2yl8X20AAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def flop(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got flop command {target}".format(target=target))
        embed = discord.Embed(
            title='Flops!',
            description=f"{ctx.author.mention} Flops on {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/zJ1AiWlhM-8AAAAd/tenor.gif',
            'https://c.tenor.com/hH4ipnIaz4AAAAAC/tenor.gif',
            'https://c.tenor.com/nwrJ8glt6BYAAAAC/tenor.gif',
            'https://c.tenor.com/vGTbtpuYDBQAAAAC/tenor.gif',
            'https://c.tenor.com/_Q_H8DveeIsAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def boop(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got boop command {target}".format(target=target))
        embed = discord.Embed(
            title='Booped!',
            description=f"{ctx.author.mention} boops {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/88HZjGgr3k0AAAAC/tenor.gif',
            'https://c.tenor.com/K8fHGmGIEZgAAAAC/tenor.gif',
            'https://c.tenor.com/Tge0mbOljJgAAAAC/tenor.gif',
            'https://c.tenor.com/l5XjHcppGN0AAAAC/tenor.gif',
            'https://media.tenor.com/oTBal8OUccQAAAAM/i-bestow-upon-you-a-boop-ollie-boop.gif',
            'https://media.tenor.com/ZJaxRmiAoOAAAAAM/boop-deadpool.gif',
            'https://c.tenor.com/uzdPAIHy_m4AAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def glare(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got glare command {target}".format(target=target))
        embed = discord.Embed(
            title='Glares!',
            description=f"{ctx.author.mention} glares at {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/Y8Ixm5imxycAAAAC/tenor.gif',
            'https://c.tenor.com/VjASosi6q7QAAAAC/tenor.gif',
            'https://c.tenor.com/aqpqnmzobw8AAAAC/tenor.gif',
            'https://c.tenor.com/_hzf0RfV_w0AAAAC/tenor.gif',
            'https://c.tenor.com/3Nrxn0XiVFcAAAAC/tenor.gif',
            'https://c.tenor.com/OEM-FiSN9-gAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def abuse(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got abuse command {target}".format(target=target))
        embed = discord.Embed(
            title='Abused!',
            description=f"{ctx.author.mention} pins {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/wOfO65zoXJMAAAAC/tenor.gif',
            'https://c.tenor.com/e88i5xynSAsAAAAC/tenor.gif',
            'https://c.tenor.com/0UVB0yt0zHMAAAAC/tenor.gif',
            'https://c.tenor.com/f7LL2S6mz0kAAAAC/tenor.gif',
            'https://c.tenor.com/2xQBxBlzwbUAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def tantrum(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got tantrum command {target}".format(target=target))
        embed = discord.Embed(
            title='Tantrum!',
            description=f"{ctx.author.mention} throws a tantrum at {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/JVdf0xu1vhIAAAAC/tenor.gif',
            'https://c.tenor.com/ygxmZXuH7SgAAAAC/tenor.gif',
            'https://c.tenor.com/nzZaJ8N8RkIAAAAC/tenor.gif',
            'https://c.tenor.com/eAZiFDaWIdoAAAAC/tenor.gif',
            'https://c.tenor.com/RYk44fvDgZkAAAAC/tenor.gif',
            'https://c.tenor.com/_uvJ4obZv1oAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @rp.command()
    async def spank(self, ctx: commands.Context, target: discord.Member) -> None:
        logger.info("Got spank command {target}".format(target=target))
        embed = discord.Embed(
            title='Spank!',
            description=f"{ctx.author.mention} spanks {target.mention}!"
        )
        url = random.choice([
            'https://c.tenor.com/KsAbF7SIY6wAAAAC/tenor.gif',
            'https://c.tenor.com/5SPNhg5O38oAAAAC/tenor.gif',
            'https://c.tenor.com/1gdTO4zudN0AAAAC/tenor.gif',
            'https://c.tenor.com/Ie6c4XTJYJcAAAAC/tenor.gif',
            'https://c.tenor.com/t7k2qjDTCrAAAAAC/tenor.gif',
            'https://c.tenor.com/tBv6AL0fyzwAAAAC/tenor.gif',
            'https://c.tenor.com/NcdgzWMhZXkAAAAC/tenor.gif',
            'https://c.tenor.com/1O7qwjzOh9EAAAAC/tenor.gif',
        ])
        embed.set_image(url=url)
        await ctx.send(embed=embed)