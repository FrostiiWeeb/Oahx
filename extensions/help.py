import discord
from discord.ext import commands
from utils.paginator import OahxPaginator

        for cog, commands in mapping.items():
           filtered = await self.filter_commands(commands, sort=True)
           command_signatures = [self.get_command_signature(c) for c in filtered]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                paginator.pages.append(discord.Embed(title=cog_name, description="\n".join(command_signatures), colour=self.context.bot.colour))

mappingproxy({'CustomDebugCog': <extensions.debug_command.CustomDebugCog object at 0xae3d2a00>, 'Misc': <extensions.misc.Misc object at 0xadf435b0>, 'Information': <extensions.information.Information object at 0xadf43580>, 'Error': <extensions.errors.Error object at 0xadf55238>, 'Owner': <extensions.owner.Owner object at 0xadef9940>, 'Help': <extensions.help.Help object at 0xa75ed970>, 'Contacts': <extensions.contacts.Contacts object at 0xa770d088>})

class Dropdown(discord.ui.Select):
    def __init__(self, ctx):
        self.context = ctx
        options = [
            discord.SelectOption(label='Misc', description='All the misc commands.'),
            discord.SelectOption(label='Information', description='All the commands for bot info.'),
            discord.SelectOption(label='Owner', description='All the commands for the owner.')
            discord.SelectOption(label="Owner", description='All the commands for contacts.')
        ]
        super().__init__(placeholder='Help', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        cog = self.context.bot.get_cog(self.values[0])
        commands = []
        for 
        pages = [discord.Embed(title=self.values[0], description=, colour=self.context.bot.colour)]
        await interaction.response.edit_message(view=self, f'Your favourite colour is {self.values[0]}')


class DropdownView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()

        self.add_item(Dropdown(ctx))

class MyHelpCommand(commands.HelpCommand):
   def get_command_signature(self, command, group_main=None):
        if group_main != None:
            return '%s%s %s %s' % (self.context.clean_prefix, group_main, command.qualified_name, command.signature)           	 
        else:
            return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)
    
   async def send_bot_help(self, mapping):
        paginator = OahxPaginator()
        paginator.pages = []       

        await paginator.paginate(self.context)           
   
   async def send_cog_help(self, cog):
        embed = discord.Embed(title=cog.qualified_name, colour=self.context.bot.colour)
        embed.add_field(name="Help", value=cog.description or "A cog, yeah")
        cmds = cog.get_commands()
        embed.add_field(name="Commands", value="\n".join([c.name if c.parent else "\n".join(self.get_command_signature(g, group_main=g.full_parent_name) for g in c.commands) for c in cog.get_commands()]), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)     
        
   async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name, colour=self.context.bot.colour)
        embed.add_field(name="Help", value="A command, yeah")
        embed.add_field(name="Sub-commands", value="\n".join([self.get_command_signature(g, group_main=g.full_parent_name) for g in group.commands]), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)                                                  

   async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), colour=self.context.bot.colour)
        embed.description = command.brief
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
        
class Help(commands.Cog):
    def __init__(self, bot, help_command):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = help_command()
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command   
        
def setup(bot):
    bot.add_cog(Help(bot, MyHelpCommand))