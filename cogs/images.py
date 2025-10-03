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

    async def quote(self, interaction: discord.Interaction, message: discord.Message):
        # Download avatar
        avatar_url = message.author.display_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status != 200:
                    return
                data = await resp.read()

        avatar = Image.open(io.BytesIO(data)).convert("RGBA")
        canvas_width, canvas_height = 1200, 630
        canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0))

        avatar = avatar.resize((canvas_width, canvas_height))
        avatar = avatar.convert("L").convert("RGBA")
        opacity = 128
        alpha = avatar.getchannel("A").point(lambda p: opacity)
        avatar.putalpha(alpha)
        canvas.paste(avatar, (0, 0))

        draw = ImageDraw.Draw(canvas)
        text = message.content
        color = (255, 255, 255)
        font_path = "data/Quicksand-Bold.ttf"

        max_width = canvas_width - 15  # padding left/right
        max_height = canvas_height - 110  # padding top/bottom
        font_size = 150
        min_font_size = 12

        # Shrink font until all lines fit width AND height
        while font_size >= min_font_size:
            font = ImageFont.truetype(font_path, font_size)
            lines = textwrap.wrap(text, width=40)  # adjust width based on font size

            # Calculate width and total height
            max_line_width = 0
            total_height = 0
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                total_height += line_height
                if line_width > max_line_width:
                    max_line_width = line_width

            if max_line_width <= max_width and total_height <= max_height:
                break
            font_size -= 2

        # Draw centered lines
        y_offset = (canvas_height - total_height) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (canvas_width - line_width) // 2
            draw.text((x, y_offset), line, font=font, fill=color)
            y_offset += line_heights[i]

        canvas.show()

    @commands.command(hidden=True)
    async def aaaa(self, ctx):
        guild_id = 1226051359066030111  # your test guild ID
        guild = discord.Object(id=guild_id)
        self.bot.tree.add_command(self.quote_ctx_menu, guild=guild)


async def setup(bot):
    await bot.add_cog(Images(bot))
