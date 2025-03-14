import discord
from database import Database
from discord import *
from datetime import datetime, timezone
from discord.ui import Button, View
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True  # Добавить эту строку

bot = commands.Bot(command_prefix="!", intents=intents)
db = Database()  # Создаем экземпляр Database

@bot.event
async def on_member_join(member):
    db.add_user(str(member.id))  # Используем метод класса Database

@bot.event
async def on_ready():
    try:
        # Сначала синхронизируем команды
        await bot.tree.sync()
        
        # Подсчет добавленных пользователей
        added_users = 0
        
        # Добавляем пользователей в БД если их там ещё нет
        for guild in bot.guilds:
            for member in guild.members:
                if not member.bot:  # Пропускаем ботов
                    if not db.get_user(str(member.id)):
                        db.add_user(str(member.id))
                        added_users += 1
        
        print(f'Бот {bot.user} успешно запущен')
        print(f'Добавлено {added_users} новых пользователей в базу данных')
        
    except Exception as e:
        print(f'Ошибка при инициализации: {str(e)}')
        
# Команда для проверки баланса
@bot.tree.command(name="balance", description="Проверить баланс")
async def balance(interaction: Interaction):
    user_data = db.get_user(str(interaction.user.id))
    if user_data is None:
        await interaction.response.send_message("Что-то пошло не так")
    else:
        await interaction.response.send_message(f"Ваш баланс: {user_data['balance']}") 
        
# Команда для получения ежедневной награды
@bot.tree.command(name="timely", description="Получить ежедневную награду")
async def timely(interaction: Interaction):
    user_data = db.get_user(str(interaction.user.id))
        
    current_time = int(datetime.now().timestamp())
    last_claim = user_data['last_claim']
    time_passed = current_time - last_claim
    
    if time_passed >= 43200:  # 12 часов в секундах
        reward = 50
        db.update_balance(str(interaction.user.id), reward, "+")
        db.update_claim_time(str(interaction.user.id))
        await interaction.response.send_message(f"Вы получили {reward} монет!")
    else:
        remaining_time = 43200 - time_passed
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        await interaction.response.send_message(
            f"Возвращайтесь через {hours} часов {minutes} минут"
        )

@bot.tree.error
async def on_error(interaction: Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}", 
        ephemeral=True
    )

bot.run(TOKEN)