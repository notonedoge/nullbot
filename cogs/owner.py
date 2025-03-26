import traceback

import discord
from discord import app_commands
from discord.ext import commands
import os
import subprocess
import embeds
import glob


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, extension: str):
        extension = extension.lower()
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
            await ctx.message.add_reaction("✅")
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, extension: str):
        extension = extension.lower()
        try:
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction("✅")
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, extension: str):
        extension = extension.lower()
        try:
            #await ctx.message.add_reaction("<a:load:1332186697823162489>")
            #await self.bot.reload_extension(f'cogs.{extension}')
            #await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
            #await ctx.message.add_reaction("✅")
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())


    @commands.command(hidden=True)
    @commands.is_owner()
    async def load_all(self, ctx):
        await ctx.message.add_reaction("<a:load:1332186697823162489>")
        for file_path in glob.glob('./cogs/**/*.py', recursive=True):
            module_name = os.path.splitext(os.path.relpath(file_path, start='./cogs'))[0].replace(os.sep, '.')
            await self.bot.load_extension(f'cogs.{module_name}')

        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
        await ctx.message.add_reaction("✅")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload_all(self, ctx):
        await ctx.message.add_reaction("<a:load:1332186697823162489>")
        for file_path in glob.glob('./cogs/**/*.py', recursive=True):
            module_name = os.path.splitext(os.path.relpath(file_path, start='./cogs'))[0].replace(os.sep, '.')
            if module_name != 'owner':
                await self.bot.unload_extension(f'cogs.{module_name}')

        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
        await ctx.message.add_reaction("✅")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        await ctx.message.add_reaction("<a:load:1332186697823162489>")
        for file_path in glob.glob('./cogs/**/*.py', recursive=True):
            module_name = os.path.splitext(os.path.relpath(file_path, start='./cogs'))[0].replace(os.sep, '.')
            await self.bot.reload_extension(f'cogs.{module_name}')

        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
        await ctx.message.add_reaction("✅")

    @commands.command(hidden=True)
    async def restart(self, ctx):
        msg = await ctx.send('now restarting')
        try:
            os.chdir('/home/echo')
            subprocess.run("./update.sh", shell=True)
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())


async def setup(bot):
    await bot.add_cog(Owner(bot))