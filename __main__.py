import os
import asyncio
import discord
from client import Batler

discord.utils.setup_logging()

intents = discord.Intents.all()
intents.members = True
activity = discord.Activity(
    type= discord.ActivityType.listening,
    name = "ваш новый запрос"
)

frank = Batler(
    intents = intents,
    activity = activity,
    data_folder= './Data/',
    config= 'config.yml'
)

frank.remove_command('help')

@frank.event
async def on_thread_update(thread):
    thread.join()

async def main():
    for f in os.listdir('./Cogs'):
        if f.endswith('.py'):
            await frank.load_extension(f'Cogs.{f[:-3]}')
    await frank.start(frank.config['DISCORD_TOKEN'])

asyncio.run(main())