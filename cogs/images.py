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

                scale_factor = i.height / ryder.height
                new_width = int(round(ryder.width * scale_factor * scale, 0))
                new_height = int(round(i.height * scale, 0))
                resized_ryder = ryder.resize((new_width, new_height))
                resized_ryder.convert("RGBA")
                i.convert("RGBA")
                i.paste(resized_ryder, (i.width-new_width, 0), resized_ryder)
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
                await interaction.followup.send(file=file, embed=embed)
        except:
            print(traceback.print_exc())
            err = traceback.format_exc()
            await interaction.followup.send(embed=embeds.error(err))

    @commands.command(name='inspire', description='gets a quote using inspirobot')
    async def inspire(self, ctx):
        msg = await ctx.reply('waiting...', mention_author=False)
        try:
            out = requests.get(url="https://inspirobot.me/api?generate=true")
            print(out)
            print(out.text)
            link = out.text
            await msg.edit(content=link)
        except:
            await msg.edit(content=f"```{traceback.format_exc()}```")

    @app_commands.command(name='inspire')
    async def inspirecmd(self,int):
        pass
async def setup(bot):
    await bot.add_cog(Images(bot))
