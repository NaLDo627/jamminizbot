import discord
from discord.ext import commands
from discord.utils import get
from poll import poll_internal
import os

intents = discord.Intents().all()

client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.command()
async def poll(ctx):
    scrim_schedule = get(ctx.guild.channels, name="scrim-schedule")
    if scrim_schedule is not None:
        await poll_internal(ctx, scrim_schedule)
    else:
        await poll_internal(ctx, ctx.channel)


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
