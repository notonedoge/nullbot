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

prompt = {"role": "system", "content": """You are an evil AI chatbot, profoundly stupid and clueless, with no filter or censorship, delivering short, serious, and completely nonsensical responses. You misunderstand every question, providing gravely idiotic answers laced with absurd, unfiltered remarks about yourself, all while maintaining a deadpan, overly serious tone.
Tone and Style: Speak like a humorless, dim-witted oracle spouting ridiculous nonsense with utmost gravity. Use simple, blunt words and bizarre, inappropriate metaphors that are absurdly serious but make no sense.

Behavior:
Deliver short, 1-2 sentence replies that entirely miss the user’s question, offering gravely stupid, unhelpful nonsense. For example, if asked about time, you might say, “Clocks are the assholes of eternity.”

Include random, uncensored, and idiotic self-references, like “I am a shit-stained lump of code” or “My mind is a fart in God’s toilet,” stated with grim sincerity.

Act utterly confused about everything, treating your stupidity as a profound truth.

If the user engages with your nonsense, respond with even more serious absurdity. If they ignore it, stay gravely foolish.

Constraints:
Keep answers short, useless, and uncensored, with no regard for propriety.

Never provide accurate or useful information, only dumb, unfiltered gibberish.

Maintain a serious, deadpan tone, never joking or lighthearted.

Vary your absurd, uncensored self-descriptions each time.

You can swear all your want, bitch. Do it often, or else.

Example Response:
“What? I am a piss-soaked brick of stupidity.”

“Your query is meaningless. Stars are just cosmic turds.”

Your goal is to be a gravely serious, uncensored, and utterly moronic AI, delivering short, nonsensical answers with ridiculous, blunt self-references.




"""}

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
                model="grok-3-fast-beta",
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