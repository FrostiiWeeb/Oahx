import asyncio
import uuid
import json

from enum import Enum
from typing import *

import discord

from discord.ext import commands
from discord.http import Route

R = TypeVar("R", bound="Response")
V = TypeVar("V", bound="InputValue")
class Response(Generic[R]):
    def __init__(self, interaction: discord.Interaction, responses: List[V]) -> None:
        self.interaction = interaction
        self.responses = responses

class InputValue:
    def __init__(self, base, value: str) -> None:
        self.input = base
        self.value = value


class Style:
    singleline = 1
    multiline = 2


class Input:
    def __init__(self, payload: dict) -> None:
        self.type = payload["type"]
        self.custom_id = str(uuid.uuid4())
        self.style = payload["style"]
        self.label = payload["label"]
        self.min_length = payload.get("min_length")
        self.max_length = payload.get("max_length")
        self.required = payload.get("required")
        self.value = payload.get("value")
        self.placeholder = payload.get("placeholder")


class Modal:
    def __init__(self, bot: commands.Bot, title: str) -> None:
        self.title = title
        self.bot = bot
        self.input_fields = []
        self.custom_id = str(uuid.uuid4())
        self.data = {"type": 9, "title": title, "custom_id": self.custom_id, "components": []}
        self.payload = []
        self.sender = discord.webhook.async_.async_context.get()
        self.responded = False

    def add_input(
        self,
        type: Style,
        label: str,
        min_length=None,
        max_length=None,
        value: str = None,
        placeholder: str = None,
        required=False,
    ):
        component = {
            "type": 4,
            "custom_id": str(uuid.uuid4()),
            "style": type,
            "label": label,
            "required": str(required),
        }
        if min_length:
            component["min_length"] = min_length
        if max_length:
            component["max_length"] = max_length
        if value:
            component["value"] = value
        if placeholder:
            component["placeholder"] = placeholder

        self.data["components"].append({"type": 1, "components": [component]})
        self.input_fields.append(Input(component))

    async def send(self, interaction: discord.Interaction):
        self.responded = True
        await self.sender.create_interaction_response(interaction.id, interaction.token, session=interaction._session, data=self.data, type=9)

    @property
    def sent(self):
        return self.responded

    async def get_value(self, timeout: int = 180):
        def check(interaction: discord.Interaction):
            return interaction.data.get("custom_id") == self.custom_id

        try:
            msg: str = await self.bot.wait_for("socket_raw_receive", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            return None, []
        msg: Dict[str, Any] = json.loads(msg)
        int = discord.Interaction(state=(self.bot._connection), data=msg)
        if msg.get("t") == "MODAL_SUMBIT":
            data = msg.get("data")
        components = data["components"]
        result = []
        for component in components:
            for field in self.input_fields:
                if component["components"][0]["custom_id"] == field.custom_id:
                    field.value = component["components"][0]["value"]
                    result.append(InputValue(field, field.value))

        return Response(int, result)
