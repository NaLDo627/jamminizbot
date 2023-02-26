import discord
from discord.ext import commands
from discord.ext.commands import Command, CommandError

class CustomHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()

    def get_command_signature(self, command):
        return f'{self.context.clean_prefix}{command.qualified_name} {command.signature}'

    def get_ending_note(self):
        return "Type !help command for more info on a command."

    async def format_command(self, command):
        async def predicate(cmd) -> bool:
            try:
                return await cmd.can_run(self.context)
            except CommandError:
                return False

        if command.hidden or not await command.can_run(self.context):
            return ''

        signature = self.get_command_signature(command)
        return f'• `{signature}`\n'

    async def send_bot_help(self, mapping):
        help_embed = discord.Embed(title="Available commands", description="These are the available commands.\n", color=discord.Color.blue())

        for cog, commands in mapping.items():
            if cog is None:
                filtered = await self.filter_commands(commands, sort=True)
                command_list = [await self.format_command(c) for c in filtered]
                if command_list:
                    help_embed.description += f"{''.join(command_list)}"
            else:
                filtered = await self.filter_commands(commands, sort=True)
                command_list = [await self.format_command(c) for c in filtered]
                if command_list:
                    help_embed.add_field(name=cog.qualified_name, value=f"{''.join(command_list)}", inline=False)

        help_embed.description += "Type `!help <command>` for more info on a command."
        channel = self.get_destination()
        await channel.send(embed=help_embed)

    async def send_command_help(self, command):
        help_embed = discord.Embed(title=self.get_command_signature(command), description=command.help, color=discord.Color.blue())

        channel = self.get_destination()
        await channel.send(embed=help_embed)