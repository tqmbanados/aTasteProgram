from functools import reduce
from time import time

from PyQt5.QtCore import pyqtSignal, QThread
from twitchio.ext import commands

import twitch_bot.token_data as token_data


class ControlBot(commands.Bot):

    def __init__(self, control_commands, signal_command, signal_start, channel_name,
                 **kwargs):
        super().__init__(token=token_data.OAUTH_TOKEN, client_id=token_data.CLIENT_ID,
                         prefix='!', nick='aTasteOfControl', initial_channels=[channel_name],
                         **kwargs)
        self.has_began = False
        self.timer = Timer()
        self.control_commands = control_commands
        self.has_ended = False
        self.signal_command = signal_command
        self.signal_start = signal_start

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.echo:
            return
        if message.content in self.control_commands:
            await self.command_recieved(message.content)
            return

        if message.author.name.lower() in token_data.ADMIN:
            await self.handle_commands(message)
        else:
            print(message)

    @commands.command()
    async def begin(self, ctx: commands.Context):
        if self.has_began:
            return
        print("Bot has began recieving commands")
        self.signal_start.emit()
        self.has_began = True
        self.timer.start()

    @commands.command()
    async def end(self, ctx: commands.Context):
        if self.has_began:
            self.has_ended = True
            self.has_began = False

    async def command_recieved(self, command):
        self.timer.new_time()
        print(command)
        volume = self.timer.get_volume()
        update_data = {'DIRECTION': 0,
                       'VOLUME': volume,
                       "COMMAND": command}
        self.signal_command.emit(update_data)


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


class Messenger(QThread):
    signal_command = pyqtSignal(dict)
    signal_start = pyqtSignal()

    def __init__(self, control_commands, channel_name):
        super().__init__()
        self.bot = ControlBot(control_commands, self.signal_command,
                              self.signal_start, channel_name)

    def run(self):
        self.bot.run()
        while not self.bot.has_ended:
            continue
        self.bot.end()


if __name__ == "__main__":
    messenger = Messenger(["TEST"])
    bot = ControlBot(["TEST"], messenger.signal_command, messenger.signal_start)
    bot.run()
