import discord
from discord import app_commands
from discord.ext import commands
import os
import platform

class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='kick')
    async def kick(self, ctx):
        try:
            embed = discord.Embed(
                title=f"{self.bot.user.name}", description=f"", color=0x194D33
            )

            embed.add_field(name=f'discord.py version', value=discord.__version__)

            delta_uptime = discord.utils.utcnow() - self.bot.startup_time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            embed.add_field(name=f'Uptime', value=f'{days}d, {hours}h, {minutes}m, {seconds}s')
            embed.add_field(name=f'Platform', value=platform.system())
            embed.add_field(name=f'{len(self.bot.cogs)} cogs loaded', value='')
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await ctx.channel.send(embed=embed)
        except Exception as e:
            await ctx.reply(e)


async def setup(bot):
    await bot.add_cog(Moderator(bot))
