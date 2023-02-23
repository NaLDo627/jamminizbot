import discord
from discord.ext import commands

intents = discord.Intents().all()

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author}!')

@client.command()
async def echo(ctx, *, message):
    await ctx.send(message)

client.run('MTA3ODI4NTAwMTIyNjk4MTM3Ng.GCIEnB.vQJNFQuAfJWQ2qxzI8r0OoOwuFt42H-qxGD23U')
