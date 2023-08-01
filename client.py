import os
import json
from json import JSONDecodeError
import discord
from discord.ext import commands


class ConfigFile:
    def __init__(self, prefix:str = '', token:str = '', # discord bot
                 yt_key: str = '', yt_playlist: str = '', yt_webhook: str = '', # youtube
                 fumo_recieve: str = '', fumo_send: str = ''): #fumo
        self.prefix = prefix
        self.token = token
        self.yt_key = yt_key
        self.yt_playlist = yt_playlist
        self.yt_webhook = yt_webhook
        self.fumo_recieve = fumo_recieve
        self.fumo_send = fumo_send


class EmptyConfig(Exception):
    def __init__(self, config_path: str):
        self.message = f'Please, set up variables in {config_path}'
        super().__init__(self.message)


class Batler(commands.Bot):
    def __init__(self, intents, activity, data_folder, config):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok= True)
        self.config_path = self.data_folder + config
        
        with open(self.config_path, 'a+', encoding="utf8") as file:
            file.seek(0)
            try:
                data = json.load(file)
                self.config = ConfigFile(**data)
                if self.config.token == "":
                    raise EmptyConfig(self.config_path)
            except JSONDecodeError:
                json.dump(ConfigFile().__dict__, file, sort_keys=False, indent=4)
                raise EmptyConfig(self.config_path)
            
        super().__init__(
            command_prefix= self.config.prefix, 
            intents= intents, 
            activity= activity
            )
        self.characters = None

    async def setup_hook(self):
        await self.tree.sync(guild = discord.Object(id=557589422372028416))

    async def on_command_error(self, ctx, error):
        print(error)