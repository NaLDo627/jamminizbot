import discord
from discord.ext import commands
from discord.utils import get
from poll import schedule_poll, poll_internal
from translate import translate_internal
from help import CustomHelpCommand
from notice import notice_internal
import os
import json

intents = discord.Intents().all()
help_command = CustomHelpCommand()
client = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

scheduled_tasks = {}
CRON_EXPRESSION_9AM_MONDAY = '0 9 * * 1'


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await client.change_presence(activity=discord.Game(name="!help"))

    if not os.path.isfile('db/schedules.txt'):
        return

    with open('db/schedules.txt', 'r') as f:
        keys = json.load(f)
        for key in keys:
            scrim_schedule_channel = client.get_channel(int(key))
            task = client.loop.create_task(schedule_poll(scrim_schedule_channel, CRON_EXPRESSION_9AM_MONDAY))
            scheduled_tasks[scrim_schedule_channel.id] = task


@client.command()
@commands.has_role('Manager')
async def schedulepoll(ctx):
    """**Register a poll for match schedule of this week at 9am Monday (manager role only)**"""
    scrim_schedule_channel = get(ctx.guild.channels, name="scrim-schedule")
    if scrim_schedule_channel is None:
        scrim_schedule_channel = ctx.channel

    if scrim_schedule_channel.id in scheduled_tasks:
        await ctx.send("There is already registered schedule.")
        return
    task = client.loop.create_task(schedule_poll(scrim_schedule_channel, CRON_EXPRESSION_9AM_MONDAY))
    scheduled_tasks[scrim_schedule_channel.id] = task

    if not os.path.exists("db"):
        os.makedirs("db")
    with open('db/schedules.txt', 'w') as f:
        json.dump(list(scheduled_tasks.keys()), f)

    await ctx.send(f"Poll scheduled. I will send a poll to `#{scrim_schedule_channel.name}` channel.")


@client.command()
@commands.has_role('Manager')
async def cancelpoll(ctx):
    """**Unregister poll at 9am Monday (manager role only)**"""
    scrim_schedule_channel = get(ctx.guild.channels, name="scrim-schedule")
    if scrim_schedule_channel is None:
        scrim_schedule_channel = ctx.channel
    if scrim_schedule_channel.id not in scheduled_tasks:
        await ctx.send("There is no registered schedule.")
        return

    scheduled_tasks[scrim_schedule_channel.id].cancel()
    del scheduled_tasks[scrim_schedule_channel.id]

    if not os.path.exists("db"):
        os.makedirs("db")
    with open('db/schedules.txt', 'w') as f:
        json.dump(list(scheduled_tasks.keys()), f)

    await ctx.send(f"Poll canceled. Poll will no longer sent to `#{scrim_schedule_channel.name}` channel.")


@client.command()
@commands.has_role('Manager')
async def notice(ctx, *, announcement):
    """**Announce to notice channel (manager role only)**

    <announcement>: the message to be announced

    It will announce to notice channel(or here if not exist) with the @everyone mention.
    It also translate your announcement to each language like `!translate` command.
    See also `!help translate`
    """
    notice_channel = get(ctx.guild.channels, name="notice")
    if notice_channel is not None:
        await notice_internal(ctx, notice_channel, announcement)
    else:
        await notice_internal(ctx, ctx.channel, announcement)


@client.command()
async def translateabove(ctx):
    """**Translate the latest message**

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
    """**Translate your message**

    <text>: the message to be translated

    It will translate if input language is:
     Korean => Japanese and English,
     Japanese => Korean and English,
     English => Japanese and Korean
    """
    await translate_internal(ctx, ctx.author, text)


@client.event
async def on_raw_reaction_add(payload):
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if message.author != client.user:
        return

    emoji = payload.emoji
    reaction = get(message.reactions, emoji=emoji)

    if reaction.count >= 6:
        message = reaction.message
        users = [user async for user in reaction.users()]
        users.remove(client.user)
        user_mentions = " ".join([f"<@{user.id}>" for user in users])

        poll_result = f"**{reaction.count-1}** Members are voted! : {reaction.emoji}"
        if reaction.count == 6:
            poll_result += "\nLet's go get a scrim."
        elif reaction.count == 9:
            poll_result = f"\nMaybe we can start a civil war."

        poll_result += f"\nMembers who reacted: {user_mentions}"
        await message.channel.send(poll_result)

discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
