import traceback
import discord
from discord.ext import commands
import yaml
from pathlib import Path


class Ryderlo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = Path('data/ryderlo.yml')
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

        with open(self.path, "r") as file:
            self.ryderlo_data = yaml.safe_load(file) or {}

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author == self.bot.user:
                return

            # Initialize user data if needed
            if message.author.id not in self.ryderlo_data:
                self.ryderlo_data[message.author.id] = {"normal": 0, "ryder": 0}

            # Check for "ryder" or mention
            content_lower = message.content.lower()
            if "ryder" in content_lower or "<@908502791373336617>" in message.content:
                # Count occurrences of "ryder" (including in words)
                words = content_lower.split()
                ryder_count = 0
                for word in words:
                    # Strip punctuation for better matching
                    clean_word = ''.join(c for c in word if c.isalnum() or c in ['<', '>', '@'])
                    if clean_word == "ryder" or clean_word == "<@908502791373336617>":
                        ryder_count += 1

                if ryder_count > 0:
                    self.ryderlo_data[message.author.id]['ryder'] += ryder_count
                else:
                    # "ryder" was in the message but not as a standalone word
                    self.ryderlo_data[message.author.id]['normal'] += 1
            else:
                self.ryderlo_data[message.author.id]['normal'] += 1

            # Save to file
            with open(self.path, "w") as file:
                yaml.safe_dump(self.ryderlo_data, file)
        except Exception:
            traceback.print_exc()



async def setup(bot):
    await bot.add_cog(Ryderlo(bot),
                      guilds=[discord.Object(id=1226051359066030111), discord.Object(id=1187525934400671814)])