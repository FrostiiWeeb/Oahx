from contextlib import redirect_stdout
from durations import Duration
from discord.ext import commands
from typing import NamedTuple
import subprocess
import functools
import datetime
import textwrap
import humanize
import asyncio
import discord
import string
import io
import re

class TimeConverter(commands.Converter):
    def convert(self, time : str):
    	try:
    		converted_time = Duration(time)
    		
    		return converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e)
    	
						