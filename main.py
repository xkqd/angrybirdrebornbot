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
        
        self.db = Database()
        super().__init__(command_prefix="!", intents=intents)

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

bot = Bot()

@bot.tree.error
async def on_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(
        f"Произошла ошибка: {str(error)}.",
        ephemeral=True
    )

bot.run(TOKEN)