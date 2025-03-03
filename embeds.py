import discord

no_permission_embed = discord.Embed(title="No permission", description="you do not have permission to run this command")
no_permission_embed.set_footer(text='this attempt has been logged.')


def image(img, time: int = None, command: str = None, user: str = None):
    embed = discord.Embed(title='', description='')
    embed.set_image(url=f'attachment://i.png')
    embed.set_footer(text=f'{command, time, user}')
    return embed


def error(content: str = None):
    if content:
        embed = discord.Embed(title="An error has occurred", description=f'`{content}`')
    else:
        embed = discord.Embed(title="An unknown error has occurred.", description="please try the command again.")
    return embed

