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

import json

from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import StreamOnlineEvent, StreamOfflineEvent




dotenv.load_dotenv()

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TARGET_SCOPES = [AuthScope.USER_READ_EMAIL]
TARGET_CHANNEL = 'xarrak99'
TOKEN_FILE = 'twitch_tokens.json'

def save_tokens(token, refresh_token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'refresh_token': refresh_token}, f)
    print("✓ Tokens saved")


def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data['token'], data['refresh_token']
    return None, None


class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch = None
        self.eventsub = None
        self.user_id = None
        self.is_live = False

    async def cog_load(self):
        """Called when cog is loaded"""
        await self.setup_twitch()

    async def cog_unload(self):
        """Cleanup when cog is unloaded"""
        await self.cleanup()

    async def cleanup(self):
        """Clean up Twitch connections"""
        try:
            if self.eventsub:
                await self.eventsub.stop()
            if self.twitch:
                await self.twitch.close()
            print("✓ Twitch connections cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    async def setup_twitch(self):
        """Initialize Twitch API and EventSub"""
        try:
            print("Setting up Twitch integration...")

            # Initialize Twitch API
            self.twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)

            # Load or authenticate tokens
            token, refresh_token = load_tokens()

            if token and refresh_token:
                print("Using saved Twitch tokens...")
                try:
                    await self.twitch.set_user_authentication(token, TARGET_SCOPES, refresh_token)
                    print("✓ Authenticated with saved tokens")
                except Exception as e:
                    print(f"Saved tokens invalid: {e}")
                    token, refresh_token = None, None

            # If no valid tokens, authenticate
            if not token:
                print("Authenticating with Twitch (browser will open)...")
                auth = UserAuthenticator(self.twitch, TARGET_SCOPES)
                token, refresh_token = await auth.authenticate()
                await self.twitch.set_user_authentication(token, TARGET_SCOPES, refresh_token)
                save_tokens(token, refresh_token)
                print("✓ Twitch authentication complete")

            # Get the user ID for the target channel
            user = await first(self.twitch.get_users(logins=[TARGET_CHANNEL]))
            if not user:
                print(f"❌ User {TARGET_CHANNEL} not found!")
                return

            self.user_id = user.id
            print(f"Found user: {user.display_name} (ID: {self.user_id})")

            # Set up EventSub WebSocket
            self.eventsub = EventSubWebsocket(self.twitch)
            self.eventsub.start()
            print("EventSub WebSocket connected")

            # Subscribe to events
            await self.eventsub.listen_stream_online(
                broadcaster_user_id=self.user_id,
                callback=self.on_stream_online
            )
            print("✓ Subscribed to stream online events")

            await self.eventsub.listen_stream_offline(
                broadcaster_user_id=self.user_id,
                callback=self.on_stream_offline
            )
            print("✓ Subscribed to stream offline events")

            print("🚀 Twitch EventSub is running!\n")

        except Exception as e:
            print(f"❌ Error setting up Twitch: {e}")
            import traceback
            traceback.print_exc()

    async def on_stream_online(self, data: StreamOnlineEvent):
        """Called when stream goes online"""
        print(f'🔴 Stream is now ONLINE!')
        print(f'   Broadcaster: {data.event.broadcaster_user_name}')
        print(f'   Started at: {data.event.started_at}')
        print(f'   Type: {data.event.type}')

        self.is_live = True

        # Send Discord notification
        channel = self.bot.get_channel(1187531474031890592)
        if channel:
            embed = discord.Embed(
                title="🔴 Stream is Live!",
                description=f"**{data.event.broadcaster_user_name}** is now streaming!",
                color=discord.Color.purple(),
                url=f"https://twitch.tv/{data.event.broadcaster_user_login}"
            )
            embed.add_field(name="Started", value=f"<t:{int(data.event.started_at.timestamp())}:R>")
            embed.add_field(name="Type", value=data.event.type.capitalize())
            embed.set_thumbnail(
                url="https://static-cdn.jtvnw.net/jtv_user_pictures/8a6381c7-d0c0-4576-b179-38bd5ce1d6af-profile_image-300x300.png")

            await channel.send(embed=embed)

    async def on_stream_offline(self, data: StreamOfflineEvent):
        """Called when stream goes offline"""
        print(f'⚫ Stream is now OFFLINE!')
        print(f'   Broadcaster: {data.event.broadcaster_user_name}')

        self.is_live = False

        # Send Discord notification
        channel = self.bot.get_channel(1187531474031890592)
        if channel:
            embed = discord.Embed(
                title="⚫ Stream Ended",
                description=f"**{data.event.broadcaster_user_name}** is now offline.",
                color=discord.Color.dark_gray()
            )
            await channel.send(embed=embed)

    @commands.command(name='livestatus')
    async def live_status(self, ctx):
        """Check if stream is currently live"""
        if self.is_live:
            await ctx.send(f"🔴 {TARGET_CHANNEL} is currently live on Twitch")
        else:
            await ctx.send(f"⚫ {TARGET_CHANNEL} is currently **offline**.")

    @commands.command(name='reloadtwitch')
    @commands.has_permissions(administrator=True)
    async def reload_twitch(self, ctx):
        """Reload Twitch integration (Admin only)"""
        await ctx.send("Reloading Twitch integration...")
        await self.cleanup()
        await self.setup_twitch()
        await ctx.send("✓ Twitch integration reloaded!")

async def setup(bot):
    await bot.add_cog(TwitchCog(bot))
