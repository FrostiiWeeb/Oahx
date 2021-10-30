import discord
from discord.ext import commands
from utils.paginator import OahxPaginator

class Trash(discord.ui.Button):
	def __init__(self, ctx, help):
		self.context = ctx
		self.help = help
		
		super().__init__(label="Trash", row=1, emoji="🗑️")
	
	async def callback(self, interaction : discord.Interaction):
		await interaction.response.edit_message("_Original message deleted_", embed=None)		

class Dropdown(discord.ui.Select):
    def __init__(self, ctx, help):
        self.context = ctx
        self.help = help
        options = [
            discord.SelectOption(label='Home', description='The main menu.', value="Home"),        
            discord.SelectOption(label='Misc', description='All the misc commands.', value="Misc"),
            discord.SelectOption(label='Information', description='All the commands for bot info.', value="Information"),
            discord.SelectOption(label='Owner', description='All the commands for the owner.', value="Owner"),
            discord.SelectOption(label='Economy', description='All the commands for economy.', value="Economy"),
            discord.SelectOption(label="Contacts", description='All the commands for contacts.', value="Contacts")
        ]
        super().__init__(placeholder='Where do you wanna go', min_values=1, custom_id="Dropdowns", max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embedd = discord.Embed(title="Help", description="```\n[] -> optional\n<> -> required```", colour=self.context.bot.colour)
        if self.values[0] == "Home":
        	await interaction.response.edit_message(embed=embedd)
        	        	        	        	
        cog = self.context.bot.get_cog(self.values[0])
        commands = []
        for command in cog.walk_commands():
        	commands.append(command)
        filtered = await self.help.filter_commands(commands, sort=True)
        command_signatures = [self.help.get_command_signature(c) for c in filtered]
        commands = "\n".join(command_signatures)               
        pages = discord.Embed(title=self.values[0], description=commands, colour=self.context.bot.colour)
        await interaction.response.edit_message(embed=pages)


class DropdownView(discord.ui.View):
    def __init__(self, ctx, help):
        super().__init__(timeout=50.0)
        self.context = ctx
        self.value = "Id"
        self.h = help


                
        supportinv = f'https://discord.gg/nHc2qRtNsU'
        botinv = 'https://discord.com/api/oauth2/authorize?client_id=844213992955707452&permissions=8&scope=bot%20applications.commands'
        self.add_item(Dropdown(ctx, help))        
        self.b1 = discord.ui.Button(label='Bot Invite', url=botinv, style = discord.ButtonStyle.blurple)         
        self.b2 = discord.ui.Button(label='Support', url=supportinv, style = discord.ButtonStyle.green)         
        self.add_item(self.b1)
        self.add_item(self.b2)
        
    
    @discord.ui.button(label='Trash', style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.value = "Yo"    	
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(embed=discord.Embed(description="_Original Message Deleted_"))
        self.remove_item(self.b1)
        self.remove_item(self.b2)
        self.remove_item(button)
        self.remove_item(Dropdown(self.context, self.h))
                

    async def interaction_check(self, interaction : discord.Interaction):
        if interaction.user and interaction.user.id in (self.context.bot.owner_ids, self.context.author.id):
            return True
        await interaction.response.send_message('This command wasnt ran by you, sorry!', ephemeral=True)
        return False
        
    async def on_timeout(self):
    	await self.message.edit('This help menu has expired', view=None, embed=None)
    	self.remove_item(Dropdown(self.context, self.h))                          

class MyHelpCommand(commands.HelpCommand):
   def get_command_signature(self, command, group_main=None):
        if group_main != None:
            return '%s%s %s %s' % (self.context.clean_prefix, group_main, command.qualified_name, command.signature)           	 
        else:
            return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)
    
   async def send_bot_help(self, mapping):
   	view = DropdownView(ctx=self.context, help=self)
   	embedd = discord.Embed(title="Help", description="```\n[] -> optional\n<> -> required```", colour=self.context.bot.colour)
   	view.message = await self.get_destination().send(embed=embedd, view=view)
#        paginator = OahxPaginator()
#        paginator.pages = []       

#        await paginator.paginate(self.context)           
   
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