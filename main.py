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
        await interaction.response.send_message(f"Ваш баланс: {user_data['balance']}") # result[1] - balance пользователя interaction.user.id из БД

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

# Команда для перевода монет другому пользователю
@bot.tree.command(name="transfer", description="Перевести монеты")
async def transfer(interaction: Interaction, target: User, amount: int):
    if amount < 1:
        await interaction.response.send_message("Сумма должна быть больше 0")
        return
    
    user_data = db.get_user(str(interaction.user.id))
    target_data = db.get_user(str(target.id))
    
    # Расчитываем комиссию и финальную сумму
    commission = int(amount * 0.1)  # 10% от суммы
    final_amount = amount - commission

    if user_data['balance'] < amount:
        await interaction.response.send_message("У вас недостаточно монет")
    else:
        db.update_balance(str(interaction.user.id), -amount)
        db.update_balance(str(target.id), final_amount)  # Используем final_amount вместо amount
        await interaction.response.send_message(
            f"Вы перевели {amount} монет\n"
            f"Комиссия: {commission} монет\n"
            f"Получатель {target.mention} получил: {final_amount} монет"
        )

@bot.tree.error
async def on_error(interaction: Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}", 
        ephemeral=True
    )

bot.run(TOKEN)