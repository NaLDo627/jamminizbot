import discord
from translate import translate_message
from discord.ext import commands
from discord.utils import get


async def notice_internal(ctx, channel_to_send, announcement):
    allowed_mentions = discord.AllowedMentions(everyone=True)
    translated_announcement = await translate_message(announcement)
    await channel_to_send.send(f"@everyone\n\n{announcement}\n\n{translated_announcement}", allowed_mentions=allowed_mentions)