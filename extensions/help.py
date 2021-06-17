import discord
from discord.ext import commands

class MyHelpCommand(commands.HelpCommand):
   def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)
    
   async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour=self.context.bot.colour)
        for cog, commands in mapping.items():
           filtered = await self.filter_commands(commands, sort=True)
           command_signatures = [self.get_command_signature(c) for c in filtered]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
        
   
   async def send_cog_help(self, cog):
        embed = discord.Embed(title=cog.qualified_name, colour=self.context.bot.colour)
        embed.add_field(name="Help", value=cog.description)
        cmds = cog.get_commands()
        filtered = await self.filter_commands(commands, sort=True)
        command_signatures = [self.get_command_signature(c) for c in filtered]      
        embed.add_field(name="Commands", value="\n".join([command for command in command_signatures]))
        channel = self.get_destination()
        await channel.send(embed=embed)                      

   async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), colour=self.context.bot.colour)
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
        
class Help(commands.Cog):
    def __init__(self, bot, help_command):
        self._original_help_command = bot.help_command
        bot.help_command = help_command()
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command   
        
def setup(bot):
    bot.add_cog(Help(bot, MyHelpCommand))