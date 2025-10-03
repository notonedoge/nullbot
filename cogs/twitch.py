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
import dotenv

import threading



dotenv.load_dotenv()

from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.eventsub.webhook import EventSubWebhook
from twitchAPI.object.eventsub import StreamOnlineEvent
from twitchAPI.object.eventsub import StreamOfflineEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope


EVENTSUB_URL = 'https://echolocation.cc/api/twitch-webhook'
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')


class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = Path('data/twitch.yml')
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

        with open(self.path, "r") as file:
            self.twitch_data = yaml.safe_load(file) or {}


        self.twitch = Twitch(CLIENT_ID, CLIENT_SECRET)

        self.eventsub = EventSubWebhook(EVENTSUB_URL, 9000, self.twitch)


    async def stream_online(self, data: StreamOnlineEvent):
        print("Received stream.online event:", data.event)
        broadcaster = data.event.broadcaster_user_name
        for channel_id, data in self.twitch_data.items():
            if broadcaster.lower() in [s.lower() for s in data.get('streams', [])]:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    await channel.send(f"{broadcaster} live")


    group = app_commands.Group(name="twitch", description="Twitch livestream notifications")

    @commands.guild_only()
    @group.command(name="add", description="Track a twitch channel")
    async def add(self, ctx, streamer_username: str, channel: discord.TextChannel):
        channel_id = str(channel.id)
        if channel_id not in self.twitch_data:
            self.twitch_data[channel_id] = {'streams': []}
        if streamer_username.lower() not in [s.lower() for s in self.twitch_data[channel_id]['streams']]:
            self.twitch_data[channel_id]['streams'].append(streamer_username)
        with open(self.path, "w") as file:
            yaml.safe_dump(self.twitch_data, file)
        await ctx.response.send_message(f"added **{streamer_username}** to notifications in {channel.mention}.")


  #  async def cog_load(self):
#
       # self.eventsub.start()
#
       # await self.twitch.authenticate_app([])
#
       # await self.eventsub.unsubscribe_all()
       # for data in self.twitch_data.values():
       #     for streamer in data.get('streams', []):
       #         user = await first(self.twitch.get_users(logins=[streamer]))
       #         if user:
       #             uid = user.id
       #             await self.eventsub.listen_stream_online(uid, self.stream_online)



async def setup(bot):
    await bot.add_cog(TwitchCog(bot))
