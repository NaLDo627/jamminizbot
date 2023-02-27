from datetime import datetime, timedelta
from pytz import timezone
import discord
from discord.utils import get
from croniter import croniter
import asyncio
from datetime import datetime


async def schedule_poll(channel_to_send, cron_schedule):
    tz = timezone('Asia/Seoul')
    while True:
        # Get the next scheduled time
        next_time = croniter(cron_schedule, datetime.now(tz)).get_next(datetime)

        # Sleep until the next scheduled time
        await asyncio.sleep((next_time - datetime.now(tz)).total_seconds())

        # Send the scheduled message
        await poll_internal(channel_to_send)


async def poll_internal(channel_to_send):
    EMOJIS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT_MORNING', 'SAT_NIGHT', 'SUN_MORNING', 'SUN_NIGHT')
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    tuesday = monday + timedelta(days=1)
    wednesday = monday + timedelta(days=2)
    thursday = monday + timedelta(days=3)
    friday = monday + timedelta(days=4)
    saturday = monday + timedelta(days=5)
    sunday = monday + timedelta(days=6)

    poll_content = f"  {get(channel_to_send.guild.emojis, name=EMOJIS[0]) if not None else EMOJIS[0]} for **MONDAY**, {monday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[1]) if not None else EMOJIS[1]} for **TUESDAY**, {tuesday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[2]) if not None else EMOJIS[2]} for **WEDNESDAY**, {wednesday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[3]) if not None else EMOJIS[3]} for **THURSDAY**, {thursday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[4]) if not None else EMOJIS[4]} for **FRIDAY**, {friday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[5]) if not None else EMOJIS[5]} for **SATURDAY (morning,daytime)**, {saturday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[6]) if not None else EMOJIS[6]} for **SATURDAY (night)**, {saturday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[7]) if not None else EMOJIS[7]} for **SUNDAY (morning,daytime)**, {sunday.strftime('%m/%d')}\n" \
                   f"  {get(channel_to_send.guild.emojis, name=EMOJIS[8]) if not None else EMOJIS[8]} for **SUNDAY (night)**, {sunday.strftime('%m/%d')}"

    league_players = get(channel_to_send.guild.roles, name="League Players")
    announcement = "Here is our schedule for this week. It will starts at 10pm at night, 10am at morning. (It can be changeable)" \
                   "\nIt will be always night at weekday(MON-FRI). " \
                   "\nPlease add a reaction below for your available time." \
                   "\nFeel free to vote even if there is already 5 people voted. " \
                   "If 8 people gathered, maybe we can start a civil war." \
                   "\n(Note that is for KST time)"
    if league_players is None:
        allowed_mentions = discord.AllowedMentions(everyone=True)
        poll_message = await channel_to_send.send(f"@everyone!\n{announcement}\n\n{poll_content}", allowed_mentions=allowed_mentions)
    else:
        poll_message = await channel_to_send.send(f"{league_players.mention}!\n{announcement}\n\n{poll_content}")
    for i in range(0, 9):
        emoji = get(channel_to_send.guild.emojis, name=EMOJIS[i])
        if emoji is not None:
            await poll_message.add_reaction(emoji)
        else:
            await poll_message.add_reaction(f"{i+1}\u20e3")
