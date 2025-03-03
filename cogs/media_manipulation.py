import random
import traceback

import discord
from discord import app_commands
from discord.ext import commands
import os
import io
import time
from PIL import Image
import requests
import embeds

ryderize_running = False


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                ryder = Image.open(os.path.abspath('./data/ryder.png'))
                w = i.height / ryder.height
                x = int(round(ryder.width * w, 0))
                size = (int(round(x * scale, 1)), int(round(i.height * scale, 1)))
                resized_ryder = ryder.resize(size)

                i.paste(ryder, (i.width-resized_ryder.width, i.height-resized_ryder.height))
                i.convert('P')

                if i.height > 1080:
                    ratio = 1080 / i.height
                    width = ratio * i.width
                    final = i.resize((1080, int(width)))
                else:
                    final = i
                final.save('i.png')
                i.close()
                file = discord.File(fp='i.png', filename='i.png')
                embed = embeds.image(img='i.png', user=interaction.user.name, command='ryderize')
                os.remove('i.png')
                await interaction.followup.send(file=file, embed=embed)
        except:
            print(traceback.print_exc())
            err = traceback.format_exc()
            await interaction.followup.send(embed=embeds.error(err))


async def setup(bot):
    await bot.add_cog(Images(bot))
