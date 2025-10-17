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
            if not self.ryderlo_data.get(message.author.id):
                self.ryderlo_data[message.author.id] = {"normal": 0, "ryder": 0}
            if "ryder" in message.content or "<@908502791373336617>" in message.content:
                words = message.content.lower().split()
                for word in words:
                    if word == "ryder" or word == "<@908502791373336617>":
                        self.ryderlo_data[message.author.id]['ryder'] += 1
            else:
                self.ryderlo_data[message.author.id]['normal'] += 1
            yaml.safe_dump(self.ryderlo_data, open(self.path, "w"))
        except:
            traceback.print_exc()

    @commands.command()
    async def ryderboard(self, ctx):
        embed = discord.Embed(title="Ryderlo Rankings", description="", color=discord.Color.green())

        plist = []
        pdata = {}
        for key, value in self.ryderlo_data.items():
            plist.append(value["ryder"]/value['normal'])
            pdata[value["ryder"]/value['normal']] = key
        plist.sort()
        for rank_index, i in enumerate(plist):
            rank = rank_index + 1
            embed.add_field(name=f"", value=f"#{rank} <@{pdata[i]}>: {i}", inline=False)
        await ctx.reply(embed=embed)



async def setup(bot):
    await bot.add_cog(Ryderlo(bot), guilds=[discord.Object(id=1226051359066030111), discord.Object(1187525934400671814)])
