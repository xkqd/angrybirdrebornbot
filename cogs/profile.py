import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="profile", description="Посмотреть профиль пользователя.")
    async def command_profile(self, interaction: Interaction, user: User = None):
        if user is None:
            user_data = self.db.get_user(str(interaction.user.id))
            user_avatar = interaction.user.avatar
            user_married_with = None
            if user_data['married_with'] != "0":
                user_married_with = interaction.guild.get_member(int(user_data['married_with']))
            embed = discord.Embed(
                title=f"Профиль — {interaction.user.name}",
                description=f"\nГолосовая активность: {user_data['voice_time']} мин.\nСообщений: {user_data['messages']}\nПартнёр: {user_married_with.mention if user_married_with != None  else "отсутствует."}",
                color=discord.Color.dark_gray()
            )

            embed.add_field(name="Монеты", value=f"```{user_data['balance']}```", inline=True)
            embed.add_field(name="Поинты", value=f"```{user_data['point_balance']}```", inline=True)

            if user_avatar is not None:
                embed.set_thumbnail(url=user_avatar.url)
            await interaction.response.send_message(embed=embed)
            return
            
        user_data = self.db.get_user(str(user.id))
        user_avatar = user.avatar
        user_married_with = None
        if user_data['married_with'] != "0":
            user_married_with = interaction.guild.get_member(int(user_data['married_with']))
        embed = discord.Embed(
                title=f"Профиль — {interaction.user.name}",
                description=f"\nГолосовая активность: {user_data['voice_time']} мин.\nСообщений: {user_data['messages']}\nПартнёр: {user_married_with.mention if user_married_with != None  else "отсутствует."}",
                color=discord.Color.dark_gray()
            )

        embed.add_field(name="Монеты", value=f"```{user_data['balance']}```", inline=True)
        embed.add_field(name="Поинты", value=f"```{user_data['point_balance']}```", inline=True)
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))