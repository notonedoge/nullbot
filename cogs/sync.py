import discord
from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def sync(self, ctx):
        fmt = await self.bot.tree.sync()
        embed = discord.Embed(title='done.', description=f'synced {len(fmt)} commands')
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=1226051359066030111), discord.Object(1187525934400671814)])
