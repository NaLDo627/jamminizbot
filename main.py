import discord
from discord.ext import commands
from discord.utils import get
from poll import SchedulePoll
from translate import translate_internal
from help import CustomHelpCommand
from notice import notice_internal
import os
from reaction_handler import ReactionHandler

intents = discord.Intents().all()
help_command = CustomHelpCommand()
client = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

schedule_poll = SchedulePoll(client)
reaction_handler = ReactionHandler(client)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await client.change_presence(activity=discord.Game(name="!help"))
    await schedule_poll.load_schedule_from_db()


@client.command()
@commands.has_role('Manager')
async def schedulepoll(ctx):
    """**Register a poll for match schedule of this week at 9am Monday (manager role only)**"""
    await schedule_poll.start_schedule(ctx)


@client.command()
@commands.has_role('Manager')
async def cancelpoll(ctx):
    """**Unregister poll at 9am Monday (manager role only)**"""
    await schedule_poll.cancel_schedule(ctx)


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
async def translatethis(ctx):
    """**Translate the original message. It should be called in reply to original message.**

    It will translate if input language is:
     Korean => Japanese and English,
     Japanese => Korean and English,
     English => Japanese and Korean

    *Note: It will not translate bot's message or command message(starting with prefix '!')
    """
    # Check if the message is a reply
    if ctx.message.reference is None:
        await ctx.send("It should be called in reply of another message to translate.")
        return

    # Get the original message object
    original_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    if original_message.author == client.user:
        await ctx.send("Sorry, bot's message will not be translated.")
        return
    elif original_message.content.startswith("!"):
        await ctx.send("Sorry, command message of bot will not be translated.")
        return

    await translate_internal(ctx, original_message.author, original_message.content)


@client.command()
async def translateabove(ctx):
    """**Translate the latest message**

    It will translate if input language is:
     Korean => Japanese and English,
     Japanese => Korean and English,
     English => Japanese and Korean

    *Note: It will not translate bot's message or command message(starting with prefix '!')
    """
    messages = [message async for message in ctx.channel.history(limit=2)]
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
    await reaction_handler.on_raw_reaction_add(payload)


@client.event
async def on_raw_reaction_remove(payload):
    await reaction_handler.on_raw_reaction_remove(payload)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to execute this command.")


discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
