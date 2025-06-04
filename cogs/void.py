import traceback
import discord
from discord.ext import commands
import json
import io
from collections import defaultdict
import re
from openai import OpenAI
import base64
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("VOID"),
    base_url="https://api.voidai.app/v1/"
)

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def image(self, ctx):
        try:
            await ctx.message.add_reaction('⏳')
            prompt = ctx.message.content
            prompt = str(prompt).removeprefix('.image')

            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt
            )

            # Access the image data directly from the 'result' object
            # The 'data' attribute typically holds a list of image objects
            # Each image object should have a 'b64_json' attribute for the base64 encoded image
            if result.data:
                image_base64 = result.data[0].b64_json # Assuming the first image is desired and it's base64 encoded
                with open("otter.png", "wb") as f:
                    f.write(base64.b64decode(image_base64))
                file = discord.File("otter.png", filename="otter.png")
                await ctx.send(file=file)
            else:
                await ctx.reply("No image data received from the API.")
            await ctx.message.clear_reactions()
        except Exception as e: # Catch a more general exception to ensure all errors are reported
            await ctx.reply(f"An error occurred: {traceback.format_exc()}")

async def setup(bot):
    await bot.add_cog(AI(bot))