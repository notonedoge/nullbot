import traceback

import discord
from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def sync(self, ctx):
        try:
            fmt = await self.bot.tree.sync()
            embed = discord.Embed(title='done.', description=f'synced {len(fmt)} commands')
            await ctx.reply(embed=embed)
        except:
            err = traceback.format_exc()
            await ctx.reply(err)

    @commands.command(hidden=True)
    async def list_commands(self, ctx):
        try:
            # Get the application ID from your bot
            app_id = self.bot.application_id

            # Fetch all global commands
            commands = await self.bot.http.get_global_commands(app_id)

            # Create an embed to display the commands
            embed = discord.Embed(title="Registered Commands", color=discord.Color.blue())
            for cmd in commands:
                embed.add_field(name=cmd['name'],
                                value=f"ID: {cmd['id']}", inline=False)

            await ctx.reply(embed=embed)
        except Exception:
            err = traceback.format_exc()
            await ctx.reply(err)


async def setup(bot):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=1226051359066030111), discord.Object(1187525934400671814)])
