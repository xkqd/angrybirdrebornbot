import discord
from discord import app_commands, Interaction, User, ui
from discord.ext import commands
from datetime import datetime

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="top", description="Проверить топ пользователей.")
    async def command_top(self, interaction: Interaction):
        # Получаем топ пользователей по балансу, сообщениям и голосовому времени и сортируем их по убыванию
        top_users_balance = sorted(self.db.get_all_users(), key=lambda x: x['balance'], reverse=True)[:10]
        top_users_messages = sorted(self.db.get_all_users(), key=lambda x: x['messages'], reverse=True)[:10]
        top_users_voice = sorted(self.db.get_all_users(), key=lambda x: x['voice_time'], reverse=True)[:10]

        class TopView(ui.Select):
            def __init__(self):
                super().__init__(placeholder="Выберите категорию.", options=[
                    discord.SelectOption(label="Баланс", value="balance"),
                    discord.SelectOption(label="Сообщения", value="messages"),
                    discord.SelectOption(label="Голосовое время", value="voice_time")
                ])

            async def callback(self, interaction: Interaction):
                if self.values[0] == "balance":
                    embed = discord.Embed(
                        title="Топ пользователей по балансу",
                        color=discord.Color.blue()
                    )
                    for index, user in enumerate(top_users_balance, start=1):
                        if user['balance'] > 0:
                            user_ = interaction.guild.get_member(int(user['user_id']))
                            embed.add_field(
                                name=f"{index}. Пользователь {user_.name}",
                                value=f"Баланс: {user['balance']} монет",
                                inline=False
                            )
                elif self.values[0] == "messages":
                    embed = discord.Embed(
                        title="Топ пользователей по сообщениям",
                        color=discord.Color.blue()
                    )
                    for index, user in enumerate(top_users_messages, start=1):
                        if user['messages'] > 0:
                            user_ = interaction.guild.get_member(int(user['user_id']))
                            embed.add_field(
                                name=f"{index}. Пользователь {user_.name}",
                               value=f"Сообщений: {user['messages']}",
                                inline=False
                            )
                elif self.values[0] == "voice_time":
                    embed = discord.Embed(
                        title="Топ пользователей по голосовому времени",
                        color=discord.Color.blue()
                    )
                    for index, user in enumerate(top_users_voice, start=1):
                        if user['voice_time'] > 0:
                            user_ = interaction.guild.get_member(int(user['user_id']))
                            embed.add_field(
                                name=f"{index}. Пользователь {user_.name}",
                                value=f"Голосовое время: {user['voice_time']} минут",
                                inline=False
                            )
                await interaction.response.edit_message(embed=embed, view=self.view)

        class TopViewTimeout(ui.View):
            def __init__(self):
                super().__init__(timeout=120)  # Тайм-аут 60 секунд
                self.add_item(TopView())
            # Отключаем шторку для выбора категории
            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                await self.message.edit(view=self)

        view = TopViewTimeout()
        await interaction.response.send_message("Выберите категорию для отображения топа:", view=view)
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Top(bot))
