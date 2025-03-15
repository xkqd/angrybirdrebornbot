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

@bot.tree.command(name="profile", description="Посмотреть профиль пользователя.")
async def command_profile(interaction: Interaction, user: User = None):
    if user is None:
        user_data = db.get_user(str(interaction.user.id))
        user_avatar = interaction.user.avatar.url
        embed = discord.Embed(
            title=f"Профиль — {interaction.user.name}",
            description=f"Баланс: {user_data['balance']} монет.\nГолосовая активность: {user_data['voice_time']} мин.",
            color=discord.Color.green()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar)
        await interaction.response.send_message(embed=embed)
        return
    user_data = db.get_user(str(user.id))
    user_avatar = user.avatar.url
    embed = discord.Embed(
        title=f"Профиль — {user.name}",
        description=f"Баланс: {user_data['balance']} монет.\nГолосовая активность: {user_data['voice_time']} мин.",
        color=discord.Color.green())
    if user_avatar is not None:
        embed.set_thumbnail(url=user_avatar)
    await interaction.response.send_message(embed=embed)
        
        
# Команда для проверки баланса
@bot.tree.command(name="balance", description="Проверить баланс.")
async def command_balance(interaction: Interaction,user: User = None):
    if user is None:
        user_data = db.get_user(str(interaction.user.id))
        user_avatar = interaction.user.avatar.url
        embed = discord.Embed(
            title=f"Баланс — {interaction.user.name}",
            description=f"Ваш баланс: {user_data['balance']} монет.",
            color=discord.Color.green()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar)
        await interaction.response.send_message(embed=embed)
        return
    user_data = db.get_user(str(user.id))
    user_avatar = user.avatar.url
    embed = discord.Embed(
        title=f"Баланс — {user.name}",
        description=f"Баланс: {user_data['balance']} монет.",
        color=discord.Color.green()
    )
    if user_avatar is not None:
        embed.set_thumbnail(url=user_avatar)
    await interaction.response.send_message(embed=embed)

# Команда для получения ежедневной награды
@bot.tree.command(name="timely", description="Получить ежедневную награду.")
async def command_timely(interaction: Interaction):
    user_data = db.get_user(str(interaction.user.id))
        
    current_time = int(datetime.now().timestamp())
    last_claim = user_data['last_claim']
    time_passed = current_time - last_claim
    # Эмбед для вывода награды
    user_avatar = interaction.user.avatar.url
    embed = discord.Embed(
                title="Ежедневная награда.",
                description="Вы получили 50 монет! Возвращайтесь через 12 часов.",
                color=discord.Color.green()
                )
    if user_avatar is not None:
        embed.set_thumbnail(url=user_avatar)
    if time_passed >= 43200:  # 12 часов в секундах
        db.update_balance(str(interaction.user.id), 50, "+")
        db.update_claim_time(str(interaction.user.id))
        await interaction.response.send_message(embed=embed)
    else:
        remaining_time = 43200 - time_passed
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        embed.description = f"Вы уже получили награду. Возвращайтесь через {hours} часов {minutes} минут."
        await interaction.response.send_message(embed=embed)

# Команда для перевода монет другому пользователю
@bot.tree.command(name="give", description="Перевести монеты другому пользователю.")
async def command_give(interaction: Interaction, target: User, amount: int):
    user_data = db.get_user(str(interaction.user.id))
    target_data = db.get_user(str(target.id))

    user_avatar = interaction.user.avatar.url

    confirm_button = Button(style=ButtonStyle.green, label="Подтвердить")
    cancel_button = Button(style=ButtonStyle.red, label="Отмена")

    buttons = View()

    # Ответ на нажатие зеленой кнопки
    async def confirm_callback(interaction: Interaction):
        if user_data['user_id'] != interaction.user.id:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка!",
                description="Вы не можете подтвердить перевод другого пользователя.",
                colour=discord.Colour.red()),ephemeral=True)
            return
        if user_data['balance'] >= amount:
            embed = discord.Embed(
                title="Успешно!",
                description=f"Вы успешно перевели пользователю {target.mention} {amount} монет. Комиссия 10% ({int(amount*0.1)} монет) удержана.",
                color=discord.Color.green()
            )
            if user_avatar is not None:
                embed.set_thumbnail(url=user_avatar)
            db.update_balance(str(interaction.user.id), amount, "-")
            db.update_balance(str(target.id), int(amount*0.9), "+")
            await interaction.response.edit_message(embed=embed,view=None)
        else:
            await interaction.response.edit_message(embed=discord.Embed(
                title="Ошибка!",
                description="У вас недостаточно монет для перевода.",
                colour=discord.Colour.red()),view=None)
            
    # Ответ на нажатие красной кнопки
    async def cancel_callback(interaction: Interaction):
        if user_data['user_id'] != interaction.user.id:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка!",
                description="Вы не можете отменить перевод другого пользователя.",
                colour=discord.Colour.red()),ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=discord.Embed(
            title="Отменено!",
            description=f"Перевод пользователю {target.mention} отменен.",
            colour=discord.Colour.red()),view=None)
    



    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback
    
    buttons.add_item(confirm_button)
    buttons.add_item(cancel_button)
    embed = discord.Embed(
            title="Подтверждение перевода.",
            description=f"Вы уверены, что хотите перевести {amount} монет пользователю {target.mention}, включая комиссию 10%?",
            color=discord.Color.green()
        )
    if user_avatar is not None: 
        embed.set_thumbnail(url=user_avatar)
    await interaction.response.send_message(embed=embed, view=buttons)

@bot.tree.error
async def on_error(interaction: Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}.", 
        ephemeral=True
    )

bot.run(TOKEN)