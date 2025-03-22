import discord
import random
import asyncio

from discord import app_commands, Interaction, User, ui
from discord.ext import commands
from datetime import datetime

devs = [1108543819370205255,749001740170559570,456802396874735616]

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="dev-addmoney",description="Панель администратора")
    async def dev_addmoney(self, interaction: Interaction, amount: int, target: User = None):

        if interaction.user.id not in devs:
            await interaction.response.send_message(embed = discord.Embed(
                        title="Панель администратора",
                        description="У вас нет доступа к этой команде.",
                        colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target is not None:
            self.db.update_balance(str(target.id),amount,"+")
            await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
            return
        self.db.update_balance(str(interaction.user.id),amount,"+")
        await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
        
    @app_commands.command(name="dev-decmoney",description="Панель администратора")
    async def dev_decmoney(self, interaction: Interaction, amount: int, target: User = None):

        if interaction.user.id not in devs:
            await interaction.response.send_message(embed = discord.Embed(
                        title="Панель администратора",
                        description="У вас нет доступа к этой команде.",
                        colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target is not None:
            self.db.update_balance(str(target.id),amount,"-")
            await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
            return
        self.db.update_balance(str(interaction.user.id),amount,"-")
        await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
        
    @app_commands.command(name="dev-addpoints",description="Панель администратора")
    async def dev_addpoints(self, interaction: Interaction, amount: int, target: User = None):

        if interaction.user.id not in devs:
            await interaction.response.send_message(embed = discord.Embed(
                        title="Панель администратора",
                        description="У вас нет доступа к этой команде.",
                        colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target is not None:
            self.db.update_points(str(target.id),amount,"+")
            await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
            return
        
        self.db.update_points(str(interaction.user.id),amount,"+")
        await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
        
    @app_commands.command(name="dev-decpoints",description="Панель администратора")
    async def dev_decpoints(self, interaction: Interaction, amount: int, target: User = None):

        if interaction.user.id not in devs:
            await interaction.response.send_message(embed = discord.Embed(
                        title="Панель администратора",
                        description="У вас нет доступа к этой команде.",
                        colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target is not None:
            self.db.update_points(str(target.id),amount,"-")
            await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
            return
        self.db.update_points(str(interaction.user.id),amount,"-")
        await interaction.response.send_message(embed=discord.Embed(
                title="Панель администратора",
                description="Успешно.",
                colour=discord.Colour.green()
            ),ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Dev(bot))