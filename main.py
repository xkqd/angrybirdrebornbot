import discord
import os

from database import Database
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.db = Database()

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'Загружен ког {filename}')
                except Exception as e:
                    print(f'Не удалось загрузить ког {filename}: {str(e)}')
        
        await self.tree.sync()
        print('Команды синхронизированы')

    async def on_ready(self):
        try:
            added_users = 0
            for guild in self.guilds:
                for member in guild.members:
                    if not member.bot and not self.db.get_user(str(member.id)):
                        self.db.add_user(str(member.id))
                        added_users += 1
            
            print(f'Bot Online')
            print(f'Добавлено {added_users} новых пользователей в базу данных')
        except Exception as e:
            print(f'Ошибка при инициализации: {str(e)}')

bot = Bot()

@bot.tree.error
async def on_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}.",
        ephemeral=True
    )

bot.run(TOKEN)