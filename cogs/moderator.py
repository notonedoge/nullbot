import traceback

import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import platform
import time

muteben = False

class KickConfirmation(ui.View):
    def __init__(self, member: discord.Member, reason: str, mod: discord.Member):
        super().__init__(timeout=60)  # 60 seconds timeout
        self.member = member
        self.reason = reason
        self.mod = mod

    @ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction, button: ui.Button):
        # Check if the user who clicked is the one who initiated
        if interaction.user.id != self.mod.id:
            await interaction.response.send_message("You're not authorized to use these buttons.", ephemeral=True)
            return

        try:
            await self.member.kick(reason=f"Kicked by {self.mod.name}: {self.reason}")

            # Update the message to show the kick was successful
            embed = discord.Embed(
                title=f"Member Kicked",
                description=f"{self.member.name} has been kicked.\nReason: {self.reason}",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)

            # Optional: Send a message to a log channel
            # if log_channel := interaction.guild.get_channel(LOG_CHANNEL_ID):
            #     await log_channel.send(f"{self.member.name} was kicked by {self.mod.name} for: {self.reason}")

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to kick this member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button: ui.Button):
        # Check if the user who clicked is the one who initiated
        if interaction.user.id != self.mod.id:
            await interaction.response.send_message("You're not authorized to use these buttons.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Kick Cancelled",
            description=f"Kick action for {self.member.name} has been cancelled.",
            color=discord.Color.dark_grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    # Handle timeout
    async def on_timeout(self):
        # This will be called when the view times out
        # We could update the message here, but we can't without the interaction object
        # So we'll just disable all buttons
        for item in self.children:
            item.disabled = True

class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name='kick')
    async def kick(self, interaction, member: discord.Member, reason: str):
        try:
            if member.top_role.position >= interaction.user.top_role.position:
                await interaction.response.send_message('You cannot kick this member', ephemeral=True)
                return

            view = KickConfirmation(member, reason, interaction.user)

            embed = discord.Embed(
                title=f"Kick {member.name}?",
                description=f"Reason: {reason}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error:\n```{traceback.format_exc()}```", ephemeral=True)



    @commands.command()
    async def ban(self, ctx, member: discord.Member, reason: str):
        await member.ban(reason=reason)
        await ctx.reply(f'banned {member.name} for {reason}')

async def setup(bot):
    await bot.add_cog(Moderator(bot))
