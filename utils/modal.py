import discord
from typing import *
from discord.ext import commands
import secrets
import asyncio

"""
{
  "title": "My Cool Modal",
  "custom_id": "cool_modal",
  "components": [{
    "type": 1,
    "components": [{
      "type": 4,
      "custom_id": "name",
      "label": "Name",
      "style": 1,
      "min_length": 1,
      "max_length": 4000,
      "placeholder": "John",
      "required": true
    }]
  }]
}
"""

class InputValue:
	def __init__(self, base, value : str) -> None:
		self.input = base
		self.value = value

class Style:
	@staticmethod
	def singleline():
		return 1

	@classmethod
	def multiline():
		return 2

class Input:
	def __init__(self, payload : dict) -> None:
		self.type = payload['type']
		self.custom_id = secrets.token_urlsafe(16)
		self.style = payload['style']
		self.label = payload['label']
		self.min_length = payload.get('min_length')
		self.max_length = payload.get('max_length')
		self.required = payload.get('required')
		self.value = payload.get('value')
		self.placeholder = payload.get('placeholder')

class Modal:
	def __init__(self, bot : commands.Bot, title : str) -> None:
		self.title = title
		self.bot = bot
		self.input_fields = []
		self.custom_id = secrets.token_urlsafe(16)
		self.data = {
          'title': title,
          'custom_id': self.custom_id,
          'components': []
        }
		self.sender = discord.webhook.async_.async_context.get()
		self.payload = []
		self.responded = False

	def input(self, type : Style, label : str, min_length = None, max_length = None, value : str = None, placeholder : str = None, required = False):
		component = {
            'type': 4,
            'custom_id': secrets.token_urlsafe(16),
            'style': type,
            'label': label,
            'required': str(required),
        }
		if min_length:
			component['min_length'] = min_length
		if max_length:
			component['max_length'] = max_length
		if value:
			component['value'] = value
		if placeholder:
			component['placeholder'] = placeholder
			
		self.data.get('components').append({
            'type': 1,
            'components': [component]
        })
		self.input_fields.append(Input(component))

	async def send(self, interaction : discord.Interaction):
		self.responded = True
		await self.sender.create_interaction_response(
            interaction_id = interaction.id,
            token = interaction.token,
            session = interaction._session,
            data = self.payload,
            type = 9
        )

	@property
	def sent(self):
		return self.responded

	async def get_value(self, wait_before_exiting: int = 180):
		def check(interaction):
			return interaction.data.get("custom_id") == self.custom_id
		try:
			msg: dict = await self.bot.wait_for('socket_raw_receive', check=check, timeout=wait_before_exiting)
		except asyncio.TimeoutError:
			return None, []
		int = discord.Interaction(state=(self.bot._get_state()), data=msg)
		if msg.get("t") == "MODAL_SUMBIT":
			data = msg.get("data")
		components = data['components']
		result = []
		for component in components:
			for field in self.fields:
				if component['components'][0]['custom_id'] == field.custom_id:
					field.value = component['components'][0]['value']
					result.append(field)
		
		return int, result