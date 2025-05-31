import discord
from discord.ext import commands
import re

emoji_pattern = r"<a?:\w+:(\d+)>"

class Ryder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != 1374903118596407418:
            return

        matches = re.findall(emoji_pattern, message.content)

        if matches:
            for emoji_id in matches:
                try:
                    emoji = await message.guild.fetch_emoji(int(emoji_id))

                    # Only allow emojis created by this specific user
                    if emoji.user and emoji.user.id != 908502791373336617:
                        await message.delete()
                        return

                except (discord.NotFound, discord.Forbidden):
                    await message.delete()
                    return

                except Exception as e:
                    print(f"Error fetching emoji: {e}")
                    return
        else:
            # No emojis found, so we check the content
            if not 'ryder' in message.content.lower():
                await message.delete()
                return

async def setup(bot):
    await bot.add_cog(Ryder(bot))
