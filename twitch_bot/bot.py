from twitchio.ext import commands
import os
from PyQt5.QtCore import QObject, pyqtSignal
import token_data
from time import time
from functools import reduce


class TasteBot(commands.Bot, QObject):
    signal_command = pyqtSignal(str)

    def __init__(self, **kwargs):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token_data.ACCESS_TOKEN, prefix='.',
                         nick='FrenBot', initial_channels=['Thyme_bb'],
                         **kwargs)
        self.has_began = False
        self.timer = Timer()

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def begin(self, ctx: commands.Context):
        if self.has_began:
            return
        self.has_began = True
        self.timer.start()

    @commands.command()
    async def control_commands(self, ctx: commands.Context):
        self.timer.new_time()
        command = ctx.message.content
        print(command)
        volume = self.timer.get_volume()
        command_data = {'RENDER': False,
                        'VOLUME': volume,
                        'SET_VOLUME': True}


class Timer:
    def __init__(self):
        self.last_time = 0
        self.time_list = []
        self.diff_list = []

    def start(self):
        self.last_time = time()
        self.time_list.append(self.last_time)

    def new_time(self):
        new = time()
        self.time_list.append(new)
        self.diff_list.append(new - self.last_time)
        self.last_time = new

    def last_values(self, idx=4):
        return self.diff_list[-idx:]

    def get_volume(self):
        diffs = self.last_values()
        if len(diffs) < 2:
            return 0.0
        return reduce(lambda x, y: x / y, diffs, 0.8)


if __name__ == "__main__":
    bot = TasteBot()
    bot.run()
