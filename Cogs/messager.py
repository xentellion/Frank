from client import Batler
import discord
import youtube
import aiohttp
from discord.ext import commands, tasks


class Messager(commands.Cog):
    def __init__(self, bot: Batler):
        self.bot = bot
        super().__init__()
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected to Discord')
        await self.youtube_playlist_getter.start()
        
    @tasks.loop(minutes=5)
    async def youtube_playlist_getter(self):
        data = await youtube.get_videos(
            self.bot.data_folder,
            self.bot.config['KEY'], 
            self.bot.config['PLAYLIST'], 
            50
        )
        if data is not None:
            if len(data) < 10:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(
                        self.bot.config["WEBHOOK"], 
                        session=session
                    )
                    for video in data:
                        await webhook.send(
                            content = f"## New video in playlist!\n⬇️  https://www.youtube.com/watch?v={video}",
                            username = "Messenger",
                            avatar_url = self.bot.user.avatar.url,
                            wait= True
                        )
                    
async def setup(bot):
    await bot.add_cog(Messager(bot))