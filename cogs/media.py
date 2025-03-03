import datetime

import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import re


class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile(
            r"https:\/\/open\.spotify\.com\/track\/[A-Za-z0-9]+|"
            r"https:\/\/open\.spotify\.com\/album\/[A-Za-z0-9]+|"
            r"music\.apple\.com\/[a-zA-Z]{2}\/album\/[a-zA-Z\d%\(\)-]+\/[\d]{1,10}\?i=[\d]{1,15}|"
            r"music\.apple\.com\/[a-zA-Z]{2}\/album\/[a-zA-Z\d%\(\)-]+\/[\d]{1,10}|"
            r"spotify\.link\/[A-Za-z0-9]+|"
            r"music\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}"
        )
        self.suppress_embed_pattern = re.compile(
            r"https:\/\/(open\.spotify\.com\/track\/[A-Za-z0-9]+|"
            r"music\.apple\.com\/[a-zA-Z]{2}\/album\/[a-zA-Z\d%\(\)-]+\/[\d]{1,10}\?i=[\d]{1,15}|"
            r"music\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11})"
        )


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if match := self.pattern.search(message.content.strip("<>")):
            link = match.group(0)
            song = requests.get(f"https://api.song.link/v1-alpha.1/links?url={link}")
            info = song.json()

            songid = info["entityUniqueId"]
            title = info["entitiesByUniqueId"][songid]["title"]
            author = info["entitiesByUniqueId"][songid]["artistName"]
            thumbnail = info["entitiesByUniqueId"][songid]["thumbnailUrl"]
            link_type = info["entitiesByUniqueId"][songid]["type"]

            view = discord.ui.View()
            if "youtubeMusic" in info["linksByPlatform"]:
                ytm = info["linksByPlatform"]["youtubeMusic"]["url"]
                ytmb = view.add_item(discord.ui.Button(url=ytm, emoji="<:ytmusic:1292307575039328390>"))
            if "youtube" in info["linksByPlatform"]:
                yt = info["linksByPlatform"]["youtube"]["url"]
                ytb = view.add_item(discord.ui.Button(url=yt, emoji="<:youtube:1292307540591251458>"))

            if "spotify" in info["linksByPlatform"]:
                spotify = info["linksByPlatform"]["spotify"]["url"]
                spotifyb = view.add_item(discord.ui.Button(url=spotify, emoji="<:spotify:1292307509985415292>"))
            if "appleMusic" in info["linksByPlatform"]:
                am = info["linksByPlatform"]["appleMusic"]["url"]
                am = view.add_item(discord.ui.Button(url=am, emoji="<:applemusic:1292307473729851412>"))

            # embed
            embed = discord.Embed(title=f"{title}", description=f'By {author}')
            if link_type == "album":
                embed.add_field(name='', value='Album')

            embed.set_thumbnail(url=thumbnail)
            if message.author.nick:
                embed.set_author(name=message.author.nick, icon_url=message.author.avatar.url)
            else:
                embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
            embed.set_footer(text=info['pageUrl'])

            if "YOUTUBE_VIDEO" not in info["entityUniqueId"] and "SPOTIFY_SONG" not in info["entityUniqueId"]:
                await message.edit(suppress=True)
            await message.reply(embed=embed, view=view, mention_author=False)


async def setup(bot):
    await bot.add_cog(Media(bot))
