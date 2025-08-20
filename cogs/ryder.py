import traceback

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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            if member.guild.id != 1187525934400671814: return
            if not member.nick:
                username = member.name
            else:
                username = member.nick
            nickname = str(f"MEGA " + username).upper()
            await member.edit(nick=nickname)
        except Exception as e:
            print(traceback.format_exc())
            c_id = 1190412893703909416
            ch = self.bot.get_channel(c_id)
            await ch.send(traceback.format_exc())

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if before.guild.id != 1187525934400671814: return
            if str(after.nick).startswith("MEGA"): return
            if before.nick != after.nick:
                if not after.nick:
                    username = after.name
                else:
                    username = after.nick
                nickname = str(f"MEGA " + username).upper()
                await before.edit(nick=nickname)
        except Exception as e:
            c_id = 1190412893703909416
            ch = self.bot.get_channel(c_id)
            await ch.send(traceback.format_exc())

    @commands.command()
    async def calculate(self, ctx):
        message_counts = {}
        await ctx.reply('Starting to count messages...')

        # We will only count messages in text channels
        text_channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]

        for channel in text_channels:
            # Send a status update
            status_message = await ctx.send(f'Processing channel: {channel.mention}')

            try:
                async for message in channel.history(limit=None):  # Use limit=None to get all messages
                    print(message.content)
                    author = message.author
                    if author not in message_counts:
                        message_counts[author] = 0
                    message_counts[author] += 1

            except discord.Forbidden:
                await status_message.edit(
                    content=f'Skipping channel {channel.mention} due to insufficient permissions.')
                continue  # Skip to the next channel if the bot can't access it

            except Exception as e:
                await status_message.edit(content=f'An error occurred in channel {channel.mention}: {e}')
                c_id = 1190412893703909416
                ch = self.bot.get_channel(c_id)
                if ch:
                    await ch.send(
                        f'Error processing channel {channel.mention}:\n```python\n{traceback.format_exc()}```')
                continue

        if not message_counts:
            return await ctx.send('No messages found in the accessible channels.')
        print(message_counts)
        sorted_counts = sorted(message_counts.items(), key=lambda item: item[1], reverse=True)

        output = "Message Counts by User:\n"
        for author, count in sorted_counts[:10]:  # Show the top 10 users
            output += f"**{author.display_name}**: {count} messages\n"

        await ctx.send(output)


async def setup(bot):
    await bot.add_cog(Ryder(bot))
