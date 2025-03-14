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
        
        print(f'Бот {bot.user} успешно запущен.')
        print(f'Добавлено {added_users} новых пользователей в базу данных.')
        
    except Exception as e:
        print(f'Ошибка при инициализации: {str(e)}')
        
# Команда для проверки баланса
@bot.tree.command(name="balance", description="Проверить баланс.")
async def command_balance(interaction: Interaction):
    user_data = db.get_user(str(interaction.user.id))
    if user_data is None:
        await interaction.response.send_message("Что-то пошло не так.")
    else:
        await interaction.response.send_message(f"Ваш баланс: {user_data['balance']}.") # result[1] - balance пользователя interaction.user.id из БД

# Команда для получения ежедневной награды
@bot.tree.command(name="timely", description="Получить ежедневную награду.")
async def command_timely(interaction: Interaction):
    user_data = db.get_user(str(interaction.user.id))
        
    current_time = int(datetime.now().timestamp())
    last_claim = user_data['last_claim']
    time_passed = current_time - last_claim
    
    if time_passed >= 43200:  # 12 часов в секундах
        db.update_balance(str(interaction.user.id), 50, "+")
        db.update_claim_time(str(interaction.user.id))
        await interaction.response.send_message(f"Вы получили 50 монет!")
    else:
        remaining_time = 43200 - time_passed
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        await interaction.response.send_message(
            f"Возвращайтесь через {hours} часов {minutes} минут."
        )

# Команда для перевода монет другому пользователю
@bot.tree.command(name="give", description="Перевести монеты.")
async def command_give(interaction: Interaction, target: User, amount: int):
    if amount < 10:
        await interaction.response.send_message("Сумма должна быть больше 9.")
        return
    
    user_data = db.get_user(str(interaction.user.id))
    # Эмбед для вывода перевода
    embed = discord.Embed(
        title="Перевод монет.",
        description=f"""Вы перевели {amount} монет пользователю {target.mention}.\n
        Комиссия: {int(amount*0.1)} монет.\n
        Получатель получит: {int(amount*0.9)} монет.""",
        color=discord.Color.green()
    )
    # Расчитываем финальную сумму
    final_amount = amount*0.9
    if user_data['balance'] < amount:
        await interaction.response.send_message("У вас недостаточно монет.",embed)
    else:
        db.update_balance(str(interaction.user.id), amount, "-")
        db.update_balance(str(target.id), final_amount, "+")
        await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.error
async def on_error(interaction: Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}.", 
        ephemeral=True
    )

bot.run(TOKEN)