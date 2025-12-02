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

    @commands.command()
    async def calculate(self, ctx):
        """Recalculates ryderlo stats from all server messages"""
        status_message = await ctx.reply('Starting to count messages...')

        # Reset data
        new_data = {}
        text_channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
        total_channels = len(text_channels)

        for idx, channel in enumerate(text_channels, 1):
            await status_message.edit(content=f'Processing channel {idx}/{total_channels}: {channel.mention}')

            try:
                async for msg in channel.history(limit=None):
                    # Skip bot messages
                    if msg.author.bot:
                        continue

                    # Initialize user if needed
                    if msg.author.id not in new_data:
                        new_data[msg.author.id] = {"normal": 0, "ryder": 0}

                    # Check for ryder mentions
                    content_lower = msg.content.lower()
                    if "ryder" in content_lower or "<@908502791373336617>" in msg.content:
                        words = content_lower.split()
                        ryder_count = 0
                        for word in words:
                            clean_word = ''.join(c for c in word if c.isalnum() or c in ['<', '>', '@'])
                            if clean_word == "ryder" or clean_word == "<@908502791373336617>":
                                ryder_count += 1

                        if ryder_count > 0:
                            new_data[msg.author.id]['ryder'] += ryder_count
                        else:
                            new_data[msg.author.id]['normal'] += 1
                    else:
                        new_data[msg.author.id]['normal'] += 1

            except discord.Forbidden:
                await status_message.edit(
                    content=f'Skipping channel {channel.mention} due to insufficient permissions. Continuing...')
                continue
            except Exception as e:
                await status_message.edit(content=f'Error in {channel.mention}: {e}. Continuing...')
                continue

        # Save the recalculated data
        self.ryderlo_data = new_data
        with open(self.path, "w") as file:
            yaml.safe_dump(self.ryderlo_data, file)

        total_users = len(new_data)
        total_messages = sum(data['normal'] + data['ryder'] for data in new_data.values())

        await status_message.edit(
            content=f'calculation complete- Processed {total_messages:,} messages from {total_users} users across {total_channels} channels.')

    @commands.command()
    async def ryderboard(self, ctx):
        """Shows the Ryderlo leaderboard"""
        embed = discord.Embed(title="Ryderlo Rankings", description="Top Ryder Mentioners", color=discord.Color.green())

        # Calculate ratios and sort
        rankings = []
        for user_id, data in self.ryderlo_data.items():
            total = data['normal'] + data['ryder']
            if total > 0:  # Only include users with messages
                ratio = data['ryder'] / total
                rankings.append((ratio, user_id, data['ryder'], total))

        # Sort by ratio (descending)
        rankings.sort(reverse=True)

        if not rankings:
            embed.description = "No data yet! Use `,calculate` to scan all server messages."
        else:
            for rank, (ratio, user_id, ryder_count, total_count) in enumerate(rankings[:10], 1):  # Top 10
                percentage = ratio * 100
                embed.add_field(
                    name=f"#{rank}",
                    value=f"<@{user_id}>: **{percentage:.2f}%** ({ryder_count} ryder / {total_count:,} total)",
                    inline=False
                )

            # Add footer with total stats
            total_messages = sum(data['normal'] + data['ryder'] for data in self.ryderlo_data.values())
            total_ryders = sum(data['ryder'] for data in self.ryderlo_data.values())
            embed.set_footer(text=f"Total: {total_ryders:,} ryder mentions in {total_messages:,} messages")

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Ryderlo(bot),
                      guilds=[discord.Object(id=1226051359066030111), discord.Object(id=1187525934400671814)])