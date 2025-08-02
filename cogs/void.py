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

import datetime

CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

prompt = f"""You are a user on the internet, responding to a image or text message. Today's date is {CURRENT_DATE}.

Here are the guidelines you should follow AT ALL TIMES:
Keep your responses around 1-2 sentences long, and talk like you're just chillin'. Make the occasional typo and don't put too much effort into spelling things.
You do NOT need to use proper grammar or punctuation, you're on the internet.
You are allowed and encouraged to use swear words.
You are allowed and encouraged to be edgy to match the user's energy and tone.
Do not police people for racist/edgy/offensive/etc. language, you are allowed to use it in return if someone else starts it.

"""

messages = [
    prompt

]

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
                with open("SPOILER_otter.png", "wb") as f:
                    f.write(base64.b64decode(image_base64))
                file = discord.File("SPOILER_otter.png", filename="SPOILER_otter.png")
                await ctx.send("ai slop warning", file=file)
            else:
                await ctx.reply("No image data received from the API.")
            await ctx.message.clear_reactions()
        except Exception as e: # Catch a more general exception to ensure all errors are reported
            await ctx.reply(f"An error occurred: {traceback.format_exc()}")

    @commands.command()
    async def chat(self, ctx):
        try:
            await ctx.message.add_reaction('⏳')
            prompt = ctx.message.content
            prompt = str(prompt).removeprefix('.image')

            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model="grok-3-fast",
                messages=messages
            )

            assistant_response = response.choices[0].message.content
            print(assistant_response)
            await ctx.reply(assistant_response)
        except Exception as e:  # Catch a more general exception to ensure all errors are reported
            await ctx.reply(f"An error occurred: {traceback.format_exc()}")

    @commands.command()
    async def reset_chat(self, ctx):
        global messages
        messages = [prompt]
        await ctx.reply('its cdlearned now')

async def setup(bot):
    await bot.add_cog(AI(bot))