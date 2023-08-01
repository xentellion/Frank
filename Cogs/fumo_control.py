from client import Batler
import discord
import youtube
import aiohttp
from client import ConfigFile
from discord.ext import commands, tasks


class Fumo(commands.Cog):
    def __init__(self, bot: Batler):
        self.bot = bot
        super().__init__()
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.fumo_recieve = await self.bot.fetch_channel(self.bot.config.fumo_recieve)
        self.fumo_target = await self.bot.fetch_channel(self.bot.config.fumo_send)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel.id == self.fumo_recieve.id:
            for item in message.attachments:
                await self.fumo_target.send(f"{item.url}")
        
async def setup(bot):        
    await bot.add_cog(Fumo(bot))