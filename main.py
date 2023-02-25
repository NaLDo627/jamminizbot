import logging

import discord
from discord.ext import commands
from discord.utils import get
from poll import poll_internal
from translate import translate_internal
from help import CustomHelpCommand
import os

intents = discord.Intents().all()

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(no_category='Commands')

client = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)
client.help_command = CustomHelpCommand()

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.command()
@commands.has_role('Manager')
async def poll(ctx):
    """Make poll (manager role only)"""
    scrim_schedule = get(ctx.guild.channels, name="scrim-schedule")
    if scrim_schedule is not None:
        await poll_internal(ctx, scrim_schedule)
    else:
        await poll_internal(ctx, ctx.channel)


@client.command()
async def translateabove(ctx):
    """Translate the latest message

    It will translate if input language is:
     Korean => Japanese and English,
     Japanese => Korean and English,
     English => Japanese and Korean

    *Note: It will not translate bot's message or command message(starting with prefix '!')
    """
    channel = ctx.channel
    messages = [message async for message in channel.history(limit=2)]
    latest_message = messages[1]
    if latest_message.author == client.user:
        await ctx.send("Sorry, bot's message will not be translated.")
        return
    elif latest_message.content.startswith("!"):
        await ctx.send("Sorry, command message of bot will not be translated.")
        return
    await translate_internal(ctx, latest_message.author, latest_message.content)


@client.command()
async def translate(ctx, *, text):
    """Translate your message

    <text>: the message to be translated

    It will translate if input language is:
     Korean => Japanese and English,
     Japanese => Korean and English,
     English => Japanese and Korean
    """
    await translate_internal(ctx, ctx.author, text)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.count >= 6:
        message = reaction.message
        users = [user async for user in reaction.users()]
        users.remove(client.user)
        user_mentions = " ".join([f"<@{user.id}>" for user in users])

        poll_result = f"**{reaction.count-1}** Members are voted! : {reaction.emoji}"
        if reaction.count == 6:
            poll_result += "\nLet's go get a scrim."
        elif reaction.count == 11:
            poll_result = f"\nMaybe we can start a civil war."

        poll_result += f"\nMembers who reacted: {user_mentions}"
        await message.channel.send(poll_result)


discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
