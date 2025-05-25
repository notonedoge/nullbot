import traceback
import discord
from discord.ext import commands
import json
import io
from collections import defaultdict
import re
from openai import OpenAI
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



    def split_into_chunks(self, text, chunk_size):
        """Split text into chunks of specified size while preserving paragraphs and code blocks."""
        if not text:
            return []

        chunks = []
        current_chunk = ""
        code_block_open = False

        # Split by lines first to preserve structure
        lines = text.split('\n')

        for line in lines:
            # Check if this line starts or ends a code block
            if '```' in line:
                code_block_count = line.count('```')
                for _ in range(code_block_count):
                    code_block_open = not code_block_open

            # If adding this line would exceed chunk size and we're not in the middle of a code block
            if len(current_chunk) + len(line) + 1 > chunk_size and not code_block_open:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'

            # If current chunk is getting too big even with code block, force split
            if len(current_chunk) > chunk_size + 100:  # Allow a little overflow for code blocks
                # Make sure we close any open code blocks
                if code_block_open:
                    current_chunk += "\n```"
                    code_block_open = False

                chunks.append(current_chunk)
                current_chunk = ""

                # If we had to split a code block, start the new chunk with a code block marker
                if code_block_open:
                    current_chunk = "```\n"

        # Add the final chunk if there's anything left
        if current_chunk:
            chunks.append(current_chunk)

        return chunks


    @commands.command()
    async def chat(self, ctx):
        content = str(ctx.message.content)
        content = content.removeprefix(".chat ").strip()
        # Skip empty messages
        if not content:
            await ctx.reply("Please provide a message to chat with the AI.")
            return

        await ctx.message.add_reaction("⏳")
        messages = [{"role": "user", "content": content}]
        response = client.chat.completions.create(
            model="gemini-2.5-flash-preview-05-20",  # An Anthropic model
            messages=messages
        )

        # Extract and print the response
        full_response = response.choices[0].message.content

        await ctx.message.clear_reactions()

        # Split response into chunks if it exceeds Discord's character limit
        if full_response.startswith("<think>"):
            full_response = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL)
            full_response = full_response.strip()
        if len(full_response) <= 2000:
            await ctx.reply(full_response)
        else:
            chunks = self.split_into_chunks(full_response, 1990)
            first_chunk = True
            for chunk in chunks:
                if first_chunk:
                    await ctx.reply(chunk)
                    first_chunk = False
                else:
                    await ctx.send(chunk)


    @commands.command()
    async def image(self, ctx):
        try:
            content = str(ctx.message.content)
            content = content.removeprefix(".image ").strip()
            await ctx.message.add_reaction("⏳")
            result = client.images.generate(
                model="gpt-image-1",
                prompt=content,
                size="1024x1024",
                quality="auto",
                n=1,
            )
            print(result)
            image_url = result.data[0].url
            await ctx.message.clear_reactions()
            await ctx.reply(image_url)
        except:
            await ctx.reply(traceback.format_exc())

async def setup(bot):
    await bot.add_cog(AI(bot))