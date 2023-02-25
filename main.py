import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta
import os

intents = discord.Intents().all()

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

# @client.command()
# async def test(ctx):
#     for channel in ctx.guild.channels:
#         if channel.name == "scrim-schedule":
#             poll_message = await channel.send(f"test")
#             await poll_message.add_reaction(f"{1}\u20e3")
#             break

async def poll_internal(ctx, channel):
    EMOJIS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT_MORNING', 'SAT_NIGHT', 'SUN_MORNING', 'SUN_NIGHT')
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    tuesday = monday + timedelta(days=1)
    wednesday = monday + timedelta(days=2)
    thursday = monday + timedelta(days=3)
    friday = monday + timedelta(days=4)
    saturday = monday + timedelta(days=5)
    sunday = monday + timedelta(days=6)

    poll_content = f"  1. {monday.strftime('%m/%d, %A')}\n" \
                   f"  2. {tuesday.strftime('%m/%d, %A')}\n" \
                   f"  3. {wednesday.strftime('%m/%d, %A')}\n" \
                   f"  4. {thursday.strftime('%m/%d, %A')}\n" \
                   f"  5. {friday.strftime('%m/%d, %A')}\n" \
                   f"  6. {saturday.strftime('%m/%d, %A')} (morning/afternoon)\n" \
                   f"  7. {saturday.strftime('%m/%d, %A')} (night)\n" \
                   f"  8. {sunday.strftime('%m/%d, %A')} (morning/afternoon)\n" \
                   f"  9. {sunday.strftime('%m/%d, %A')} (night)"

    league_players = get(ctx.guild.roles, name="League Players")
    if league_players is None:
        allowed_mentions = discord.AllowedMentions(everyone=True)
        poll_message = await channel.send(f"@everyone! Here is our schedule for this week:\n{poll_content}", allowed_mentions=allowed_mentions)
    else:
        poll_message = await channel.send(f"{league_players.mention}! Here is our schedule for this week:\n{poll_content}")
    for i in range(0, 9):
        emoji = get(client.emojis, name=EMOJIS[i])
        if emoji is not None:
            await poll_message.add_reaction(emoji)
        else:
            await poll_message.add_reaction(f"{i+1}\u20e3")
@client.command()
async def poll(ctx):
    scrim_schedule = get(ctx.guild.channels, name="scrim-schedule")
    if scrim_schedule is not None:
        await poll_internal(ctx, scrim_schedule)
    else:
        await poll_internal(ctx, ctx.channel)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.count == 6 or reaction.count == 11:
        message = reaction.message
        users = [user async for user in reaction.users()]
        users.remove(client.user)
        user_mentions = " ".join([f"<@{user.id}>" for user in users])

        if reaction.count == 6:
            poll_result = f"**5** Members voted! : {reaction.emoji} ({reaction.count-1} votes)\nLet's go get a scrim."
        elif reaction.count == 11:
            poll_result = f"**10** Members voted! : {reaction.emoji} ({reaction.count-1} votes)\nMaybe we can start a civil war."
        else:
            return

        poll_result += f"\nMembers who reacted: {user_mentions}"
        await message.channel.send(poll_result)


discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
