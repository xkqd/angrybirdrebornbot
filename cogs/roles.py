import discord
from discord import app_commands, Interaction
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="create_role", description="Создать собственную роль.")
    async def command_create_role(self, interaction: Interaction):
        # Создаем модальное окно
        class RoleCreationModal(discord.ui.Modal, title="Создание роли"):
            role_name = discord.ui.TextInput(
                label="Название роли",
                placeholder="Введите название роли",
                max_length=30,
                required=True,
                row=1
            )
            role_colour = discord.ui.TextInput(
                label="Цвет роли (HEX)",
                placeholder="#FF5733",
                max_length=7,
                required=True,
                row=2
            )

            async def on_submit(self, interaction: Interaction):
                guild = interaction.guild
                existing_role = discord.utils.get(guild.roles, name=self.role_name.value)

                if existing_role:
                    await interaction.response.send_message(
                        f"Роль с именем '{self.role_name.value}' уже существует.", ephemeral=True
                    )
                    return

                # Проверяем корректность цвета
                try:
                    color = discord.Color(int(self.role_colour.value.lstrip('#'), 16))
                except ValueError:
                    await interaction.response.send_message(
                        "Неверный формат цвета. Используйте HEX-код (например, #FF5733).", ephemeral=True
                    )
                    return

                # Создаем роль
                new_role = await guild.create_role(name=self.role_name.value, color=color)
                await interaction.user.add_roles(new_role)
                await interaction.response.send_message(
                    f"Роль '{new_role.name}' успешно создана с цветом {self.role_colour.value} и добавлена вам.", ephemeral=True
                )

        # Отправляем модальное окно пользователю
        await interaction.response.send_modal(RoleCreationModal())

async def setup(bot):
    await bot.add_cog(Roles(bot))