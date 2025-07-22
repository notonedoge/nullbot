import datetime
import traceback

import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import re

song_cache = {}

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile(
            r"https:\/\/(open\.spotify\.com\/track\/[A-Za-z0-9]+|"
            r"(http://|https://)?(?:geo\.)?music\.apple\.com\/[a-zA-Z]{2}\/(?:album|song)\/[^\/]+\/\d+(?:\?[^\s]*)?|"
            r"spotify\.link\/[A-Za-z0-9]+|"
            r"youtu\.be\/[A-Za-z0-9_-]{11}|"
            r"(?:www\.|m\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}|"
            r"music\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11})"
        )

        self.suppress_embed_pattern = re.compile(
            r"https:\/\/(open\.spotify\.com\/track\/[A-Za-z0-9]+|"
            r"(http://|https://)?(?:geo\.)?music\.apple\.com\/[a-zA-Z]{2}\/(?:album|song)\/[^\/]+\/\d+(?:\?[^\s]*)?|"
            r"music\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11})"
        )


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if match := self.pattern.search(message.content.strip("<>")):
                await message.add_reaction("⏳")
                link = match.group(0)
                if link in song_cache:
                    song = song_cache[link]
                else:
                    song = requests.get(f"https://api.song.link/v1-alpha.1/links?url={link}")
                    song_cache[link] = song
                info = song.json()

                songid = info["entityUniqueId"]
                title = info["entitiesByUniqueId"][songid]["title"]
                author = info["entitiesByUniqueId"][songid]["artistName"]
                thumbnail = info["entitiesByUniqueId"][songid]["thumbnailUrl"]
                link_type = info["entitiesByUniqueId"][songid]["type"]

                if "youtube" in match.group(0) or "youtu.be" in match.group(0):
                    if 'spotify' not in info.get('linksByPlatform', {}):
                        await message.clear_reactions()
                        return

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
                await message.clear_reaction("⏳")

        except:
            log = traceback.format_exc()
            await message.reply(f"```{log}```")


    @commands.command(hidden=True)
    async def clear_songs(self, ctx):
        song_cache.clear()
        await ctx.reply("Cache cleared.")

    @commands.command()
    async def linksong(self, ctx):
        try:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if match := self.pattern.search(message.content.strip("<>")):
                await message.add_reaction("⏳")
                link = match.group(0)
                if link in song_cache:
                    song = song_cache[link]
                else:
                    song = requests.get(f"https://api.song.link/v1-alpha.1/links?url={link}")
                    song_cache[link] = song
                info = song.json()

                songid = info["entityUniqueId"]
                title = info["entitiesByUniqueId"][songid]["title"]
                author = info["entitiesByUniqueId"][songid]["artistName"]
                thumbnail = info["entitiesByUniqueId"][songid]["thumbnailUrl"]
                link_type = info["entitiesByUniqueId"][songid]["type"]

                if "youtube" in match.group(0) or "youtu.be" in match.group(0):
                    if 'spotify' not in info.get('linksByPlatform', {}):
                        await message.clear_reactions()
                        return

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
                await message.clear_reaction("⏳")

        except:
            log = traceback.format_exc()
            await ctx.reply(f"```{log}```")


async def setup(bot):
    await bot.add_cog(Media(bot))
