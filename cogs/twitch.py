import discord
from discord import app_commands
from discord.ext import commands
import os
import platform
import subprocess
import sys
import asyncio
import yaml
from pathlib import Path


class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = Path('data/twitch.yml')
        if not self.path.exists():
            self.path.touch()
        with open("data/twitch.yml", "r") as file:
            self.twitch_data = yaml.safe_load(file)




    group = app_commands.Group(name="twitch", description="Twitch livestream notifications")

    @group.command(name="add", description="Track a twitch channel")
    async def add(self, ctx, streamer_username: str, channel: discord.TextChannel):
        channel_id = str(channel.id)
        if channel_id not in self.twitch_data:
            print('new channel.')
            self.twitch_data[channel_id] = {'streams': []}
        self.twitch_data[channel_id]['streams'].append(streamer_username)
        await ctx.response.send_message('Added channel.')





async def setup(bot):
    await bot.add_cog(Twitch(bot))
