import discord
from discord.ext import commands
from datetime import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            added_users = 0
            for guild in self.bot.guilds:
                for member in guild.members:
                    if not member.bot and not self.db.get_user(str(member.id)):
                        self.db.add_user(str(member.id))
                        added_users += 1
                    if member.voice is not None:
                        self.db.update_last_voice_time(str(member.id))
            
            print(f'Bot Online')
            print(f'Добавлено {added_users} новых пользователей в базу данных')
        except Exception as e:
            print(f'Ошибка при инициализации: {str(e)}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        self.db.add_message_to_counter(str(message.author.id))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:  # Пропускаем ботов
            return
        
        if before.channel is None and after.self_deaf is False:  # Пользователь зашел в голосовой канал не замученным
            self.db.update_last_voice_time(str(member.id))
            return
        
        if before.self_deaf is True and after.self_deaf is False:  # Пользователь размутился
            self.db.update_last_voice_time(str(member.id))
            return
        
        if before.self_deaf is False and after.self_deaf is True:  # Пользователь замутился
            self.db.update_voice_time(str(member.id))
            self.db.update_last_voice_time(str(member.id))
            return
        
        if before.channel and after.channel is None: 
            self.db.update_voice_time(str(member.id))     
            return
        
        if before.channel and before.channel.id == 1329128817452908646:
            return

async def setup(bot):
    await bot.add_cog(Events(bot))