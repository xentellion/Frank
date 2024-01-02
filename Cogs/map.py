import math
import io
import cv2
import yaml
import random
import discord
import pandas as pd
import numpy as np
from discord.ext import commands


class MagnaNavigator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @commands.command(name='map') 
    async def navigate(self, ctx, start, end):
        async with ctx.typing():
            names, matrix, = self.load_map(self.bot.data_folder + 'magnaweb.csv')
            self.coords = pd.read_csv(self.bot.data_folder + 'coords.csv', sep=',')
            try:
                start_idx = names.index(start)
                end_idx = names.index(end)
            except ValueError:
                await ctx.send("Маршрут не найден")
                return
            map_city, buffer = await self.plot_map(ctx, start_idx, end_idx, names, matrix)
            file = None
            with io.BytesIO(buffer) as bytes :
                file= discord.File(
                    bytes, filename='map.png'
                )
            text = f'🟦 Начало маршрута - `{map_city[0]}`\n🟩 Конец маршрута - `{map_city[-1]}`\n\n **Путь:**\n'
            for i in map_city:
                text += f'`{i}`— '    
            text = text[:-2] + '\n\n'
            l = len(map_city)
            if l // 5 > 1:
                with open(self.bot.data_folder + 'random_enc.yml', 'r', encoding="utf8") as f:
                    r_inc = yaml.safe_load(f)
                for i in range(l // 5):
                    text +="```diff\n"
                    r = random.choice(list(r_inc.keys()))
                    if  r == 'around':
                        before = random.randint(0,1)
                        text += f"-На участке маршрута {'перед осколком' if before else 'после осколка'}\
                            {random.choice(map_city[1:-1])} {random.choice(list(r_inc.get('around')))}```"
                    elif r == 'on_shard':
                        text += f"-На участке маршрута пролетающем через осколок \
                            {random.choice(map_city[1:-1])} {random.choice(list(r_inc.get('on_shard')))}```"
            if '1' in map_city:
                text +="```diff\n"
                text +="+Маршрут проложен через Ядро Нокс-Cити. Требуется корпоративное разрешение. Ваш запрос передан \
                    корпорации Магнакорп.```"
                                    
            embed = discord.Embed(
                title = "МАРШРУТ ПОСТРОЕН",
                description = text,
                color = discord.Color.blue()
            )
            embed.set_image(url = 'attachment://map.png')
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/1137346239931883530/1137346240145805433/0.png?width=398&height=398')
        await ctx.send(file= file, embed=embed)

    async def plot_map(self, ctx, start_idx, end_idx, names, matrix):
        path = self.calculate_path(matrix, start_idx, end_idx)
        res = [names[idx] for idx in path]
        img = cv2.imread(self.bot.data_folder + 'map.png', cv2.IMREAD_UNCHANGED)
        for idx in range(len(path) - 1):
            img = cv2.line(img, 
                (self.coords.at[path[idx], 'x'], self.coords.at[path[idx], 'y']), 
                (self.coords.at[path[idx+1], 'x'], self.coords.at[path[idx+1], 'y']), 
                (0, 0, 255), 10)
        for idx in range(len(path)):
            img = cv2.circle(img, 
                (self.coords.at[path[idx], 'x'], self.coords.at[path[idx], 'y']),
                10, (0, 255, 255), -1)
        half_side = 20
        img = cv2.rectangle(img, 
            (self.coords.at[path[0], 'x'] - half_side, self.coords.at[path[0], 'y'] - half_side),
            (self.coords.at[path[0], 'x'] + half_side, self.coords.at[path[0], 'y'] + half_side),
            (255, 0, 0), -1)
        img = cv2.rectangle(img, 
            (self.coords.at[path[-1], 'x'] - half_side, self.coords.at[path[-1], 'y'] - half_side),
            (self.coords.at[path[-1], 'x'] + half_side, self.coords.at[path[-1], 'y'] + half_side),
            (0, 255, 0), -1)
        is_success, buffer = cv2.imencode(".png", img)
        return res,buffer
        
    def load_map(self, path):
        df = pd.read_csv(path, sep=',')
        df = df.drop(df.columns[0], axis=1)
        arr = df.to_numpy()
        arr = np.triu(arr) + np.tril(arr.T)
        arr = np.nan_to_num(arr, nan=np.inf)
        return (df.columns.tolist(), arr.tolist())
        
    def calculate_path(self, matrix, start_node, end_node):
        map_path = self.dijkstra(matrix, int(start_node), int(end_node))
        start = int(start_node)
        end = int(end_node)
        result = [end]
        while end != start:
            end = map_path[result[-1]]
            result.append(end)
        result.reverse()
        return result

    def dijkstra(self, matrix, start_node:int, end_node:int):
        node_count = len(matrix) 
        path_length = [math.inf]*node_count

        current_node = start_node
        visited_nodes = {current_node}
        path_length[current_node] = 0
        map_path = [0]*node_count

        while current_node != -1:
            for node, path_weight in enumerate(matrix[current_node]): 
                if node not in visited_nodes:
                    new_weight = path_length[current_node] + path_weight + self.heuristics(current_node, end_node)
                    if new_weight < path_length[node]:
                        path_length[node] = new_weight
                        map_path[node] = current_node

            current_node = self.arg_min(path_length, visited_nodes) 
            if current_node >= 0:
                visited_nodes.add(current_node)
            
            if current_node == end_node:
                break
        
        return map_path
        
    def arg_min(self, T, S):
        amin = -1
        max = math.inf
        for i, t in enumerate(T):
            if t < max and i not in S:
                max = t
                amin = i
        return amin
    
    def heuristics(self, point1, point2):
        p1 = self.coords.loc[point1]
        p2 = self.coords.loc[point2]
        dist = abs(p1.at['x']-p2.at['x']) + abs(p1.at['y']-p2.at['y'])
        return dist/4000
    
async def setup(bot):        
    await bot.add_cog(MagnaNavigator(bot))