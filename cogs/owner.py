import sys
import traceback
import git
import discord
from discord import app_commands
from discord.ext import commands
import os
import subprocess
import embeds
import glob
import yaml


with open("data.yml", "r") as file:
    data = yaml.safe_load(file)


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
            fmt = await self.bot.tree.sync(guild=ctx.guild)
            guild_cmd = await self.bot.tree.sync(guild=discord.Object(id=1187525934400671814))

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
            fmt = await self.bot.tree.sync(guild=ctx.guild)
            guild_cmd = await self.bot.tree.sync(guild=discord.Object(id=1187525934400671814))
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())


    @commands.command(hidden=True)
    @commands.is_owner()
    async def load_all(self, ctx):
        await ctx.message.add_reaction("<a:load:1332186697823162489>")
        for file_path in glob.glob('./cogs/**/*.py', recursive=True):
            module_name = os.path.splitext(os.path.relpath(file_path, start='./cogs'))[0].replace(os.sep, '.')
            await self.bot.load_extension(f'cogs.{module_name}')

        fmt = await self.bot.tree.sync(guild=ctx.guild)
        guild_cmd = await self.bot.tree.sync(guild=discord.Object(id=1187525934400671814))
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

        fmt = await self.bot.tree.sync(guild=ctx.guild)
        guild_cmd = await self.bot.tree.sync(guild=discord.Object(id=1187525934400671814))
        await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
        await ctx.message.add_reaction("✅")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        await ctx.message.add_reaction("<a:load:1332186697823162489>")
        for file_path in glob.glob('./cogs/**/*.py', recursive=True):
            module_name = os.path.splitext(os.path.relpath(file_path, start='./cogs'))[0].replace(os.sep, '.')
            await self.bot.reload_extension(f'cogs.{module_name}')

        fmt = await self.bot.tree.sync(guild=ctx.guild)
        guild_cmd = await self.bot.tree.sync(guild=discord.Object(id=1187525934400671814))
        await ctx.message.remove_reaction("<a:load:1332186697823162489>", self.bot.user)
        await ctx.message.add_reaction("✅")

    @commands.command(hidden=True)
    async def restart(self, ctx):
        msg = await ctx.send('now restarting')
        try:
            g = git.cmd.Git(os.getcwd())
            g.pull()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            await ctx.reply(embed=embeds.error(traceback.format_exc()), content=traceback.print_exc())

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, count: int):
        if count > 100:
            await ctx.send('value too large. (max 100)')
        elif count < 1:
            for number in range(1, count):
                await ctx.send('message')
        else:
            await ctx.channel.purge(limit=count + 1)
            channel_id = data[ctx.guild.id]["message_log"]
            channel = self.bot.get_channel(channel_id)
            s = "s"
            if count == 1:
                s = ""
            embed = discord.Embed(title=f'{count} Message{s} Purged')
            embed.add_field(name=f'Sent by', value={ctx.author.user.name})
            await channel.send(embed=embed)



    @commands.command()
    async def ccg(self, ctx):
        try:
            await self.bot.tree.clear_commands(guild=None)
            await ctx.reply('tst')
        except:
            await ctx.reply(traceback.format_exc())
        await ctx.reply('tst')

async def setup(bot):
    await bot.add_cog(Owner(bot))