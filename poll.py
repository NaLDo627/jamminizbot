from datetime import datetime, timedelta
from pytz import timezone
import discord
from discord.utils import get
from croniter import croniter
import asyncio
import fileutil


class SchedulePoll:
    def __init__(self, client):
        self.client = client
        self.tz = timezone('Asia/Seoul')
        self.scheduled_tasks = {}
        self.EMOJIS = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT_MORNING', 'SAT_NIGHT', 'SUN_MORNING', 'SUN_NIGHT')
        self.CRON_EXPRESSION_9AM_MONDAY = '0 9 * * 1'
        self.SCHEDULES_FILE_PATH = 'db/schedules.txt'

    async def load_schedule_from_db(self):
        keys = fileutil.read_from_file(self.SCHEDULES_FILE_PATH)
        if keys is not None:
            for key in keys:
                scrim_schedule_channel = self.client.get_channel(int(key))
                await self._create_poll_schedule(scrim_schedule_channel)

    async def start_schedule(self, ctx):
        scrim_schedule_channel = get(ctx.guild.channels, name="scrim-schedule")
        if scrim_schedule_channel is None:
            scrim_schedule_channel = ctx.channel

        if scrim_schedule_channel.id in self.scheduled_tasks:
            await ctx.send("There is already registered schedule.")
            return

        await self._create_poll_schedule(scrim_schedule_channel, save_to_db=True)
        await ctx.send(f"Poll scheduled. I will send a poll to `#{scrim_schedule_channel.name}` channel.")

    async def _create_poll_schedule(self, channel_to_send, save_to_db=False):
        task = self.client.loop.create_task(self._start(channel_to_send))
        self.scheduled_tasks[channel_to_send.id] = task

        if save_to_db is True:
            fileutil.write_to_json(self.SCHEDULES_FILE_PATH, list(self.scheduled_tasks.keys()))

    async def _start(self, channel_to_send):
        while True:
            # Get the next scheduled time
            next_time = croniter(self.CRON_EXPRESSION_9AM_MONDAY, datetime.now(self.tz)).get_next(datetime)

            # Sleep until the next scheduled time
            await asyncio.sleep((next_time - datetime.now(self.tz)).total_seconds())

            # Send the scheduled message
            await self._poll_internal(channel_to_send)

    async def _poll_internal(self, channel_to_send):
        today = datetime.today()
        monday = today - timedelta(days=today.weekday())
        tuesday = monday + timedelta(days=1)
        wednesday = monday + timedelta(days=2)
        thursday = monday + timedelta(days=3)
        friday = monday + timedelta(days=4)
        saturday = monday + timedelta(days=5)
        sunday = monday + timedelta(days=6)

        poll_content = f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[0]) if not None else self.EMOJIS[0]} for **MONDAY**, {monday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[1]) if not None else self.EMOJIS[1]} for **TUESDAY**, {tuesday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[2]) if not None else self.EMOJIS[2]} for **WEDNESDAY**, {wednesday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[3]) if not None else self.EMOJIS[3]} for **THURSDAY**, {thursday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[4]) if not None else self.EMOJIS[4]} for **FRIDAY**, {friday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[5]) if not None else self.EMOJIS[5]} for **SATURDAY (morning,daytime)**, {saturday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[6]) if not None else self.EMOJIS[6]} for **SATURDAY (night)**, {saturday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[7]) if not None else self.EMOJIS[7]} for **SUNDAY (morning,daytime)**, {sunday.strftime('%m/%d')}\n" \
                       f"  {get(channel_to_send.guild.emojis, name=self.EMOJIS[8]) if not None else self.EMOJIS[8]} for **SUNDAY (night)**, {sunday.strftime('%m/%d')}"

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
            emoji = get(channel_to_send.guild.emojis, name=self.EMOJIS[i])
            if emoji is not None:
                await poll_message.add_reaction(emoji)
            else:
                await poll_message.add_reaction(f"{i+1}\u20e3")

    async def cancel_schedule(self, ctx):
        scrim_schedule_channel = get(ctx.guild.channels, name="scrim-schedule")
        if scrim_schedule_channel is None:
            scrim_schedule_channel = ctx.channel

        if scrim_schedule_channel.id not in self.scheduled_tasks:
            await ctx.send("There is no registered schedule.")
            return

        self.scheduled_tasks[scrim_schedule_channel.id].cancel()
        del self.scheduled_tasks[scrim_schedule_channel.id]

        fileutil.write_to_json('db/schedules.txt', list(self.scheduled_tasks.keys()))
        await ctx.send(f"Poll canceled. Poll will no longer sent to `#{scrim_schedule_channel.name}` channel.")