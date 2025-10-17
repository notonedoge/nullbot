import random
import traceback

import discord
from discord import app_commands
from discord.ext import commands
import os
import io
import time
import textwrap
from PIL import Image, ImageDraw, ImageFont
import requests
import embeds
import aiohttp

ryderize_running = False


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.quote_ctx_menu = app_commands.ContextMenu(name="Quote it", callback=self.quote)
        self.bot.tree.add_command(self.quote_ctx_menu)

    @commands.command(brief="Resets ryderize if broken", hidden=True)
    async def re(self, ctx):
        global ryderize_running
        ryderize_running = False



    @app_commands.command(name='ryderize', description='adds a photo of ryder/ pointing to an image')
    async def ryderize(self, interaction, image: discord.Attachment, scale: float = 1.0):
        await interaction.response.defer()
        try:
            img = await image.read()
            with Image.open(io.BytesIO(img)) as i:
                # Convert base image to RGBA
                i = i.convert("RGBA")

                # Open and convert ryder image to RGBA
                ryder = Image.open(os.path.abspath('./data/ryder.png')).convert("RGBA")

                # Scale ryder to match the height of the input image (accounting for custom scale)
                scale_factor = i.height / ryder.height
                new_width = int(round(ryder.width * scale_factor * scale))
                new_height = int(round(ryder.height * scale_factor * scale))  # This scales proportionately
                resized_ryder = ryder.resize((new_width, new_height))

                # Position ryder on the right side
                i.paste(resized_ryder, (i.width - new_width, 0), resized_ryder)

                # Resize if too large (maintaining aspect ratio)
                if i.height > 1080:
                    ratio = 1080 / i.height
                    new_width = int(i.width * ratio)
                    final = i.resize((new_width, 1080))
                else:
                    final = i

                final.save('i.png')
                file = discord.File(fp='i.png', filename='i.png')
                embed = embeds.image(img='i.png', user=interaction.user.name, command='ryderize')
                await interaction.followup.send(file=file, embed=embed)
        except Exception as e:
            print(traceback.print_exc())
            err = traceback.format_exc()
            await interaction.followup.send(embed=embeds.error(err))

    @commands.command(name='inspire', description='be inspired')
    async def inspire(self, ctx):
        msg = await ctx.reply('waiting...', mention_author=False)
        try:
            out = requests.get(url="https://inspirobot.me/api?generate=true")
            link = out.text
            await msg.edit(content=link)
        except:
            await msg.edit(content=f"```{traceback.format_exc()}```")

    @app_commands.command(name='inspire', description='gets a quote using inspirobot')
    async def inspirecmd(self, ctx):
        try:
            out = requests.get(url="https://inspirobot.me/api?generate=true")
            link = out.text
            await ctx.response.send_message(link)
        except:
            await ctx.response.send_message(content=f"```{traceback.format_exc()}```")


    @commands.command(hidden=True)
    async def aaaa(self, ctx):
        guild_id = 1226051359066030111  # your test guild ID
        guild = discord.Object(id=guild_id)
        self.bot.tree.add_command(self.quote_ctx_menu, guild=guild)


async def setup(bot):
    await bot.add_cog(Images(bot))
