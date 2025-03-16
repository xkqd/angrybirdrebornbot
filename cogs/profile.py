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
            embed = discord.Embed(
                title=f"Профиль — {interaction.user.name}",
                description=f"\nГолосовая активность: {user_data['voice_time']} мин.\nСообщений: {user_data['messages']}",
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
        embed = discord.Embed(
            title=f"Профиль — {user.name}",
            description=f"Баланс: {user_data['balance']} <a:coins:1350287791254274078>\nГолосовая активность: {user_data['voice_time']} мин.",
            color=discord.Color.green())
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))