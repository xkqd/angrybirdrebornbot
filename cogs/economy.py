import discord
import random
import asyncio

from discord import app_commands, Interaction, User, ui
from discord.ext import commands
from datetime import datetime

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="balance", description="Проверить баланс.")
    async def command_balance(self, interaction: Interaction, user: User = None):
        if user is None:
            user = interaction.user
        user_data = self.db.get_user(str(user.id))
        user_avatar = user.avatar
        embed = discord.Embed(
            title=f"Баланс — {user.name}",
            color=discord.Color.dark_gray()
        )
        if user.bot:
            await interaction.response.send_message(embed=discord.Embed(
                title="Баланс",
                description="Вы не можете проверить баланс бота.",
                colour=discord.Colour.red()
                ),ephemeral=True)
            return
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)
        
        embed.add_field(name="Монеты", value=f"```{user_data['balance']}```", inline=True)
        embed.add_field(name="Поинты", value=f"```{user_data['point_balance']}```", inline=True)

        await interaction.response.send_message(embed=embed)


    # Команда для получения ежедневной награды
    @app_commands.command(name="timely", description="Получить ежедневную награду.")
    async def command_timely(self, interaction: Interaction):
        user_data = self.db.get_user(str(interaction.user.id))
            
        current_time = int(datetime.now().timestamp())
        last_claim = user_data['last_claim']
        time_passed = current_time - last_claim
        # Эмбед для вывода награды
        user_avatar = interaction.user.avatar
        next_claim_time2 = current_time + 43200
        embed = discord.Embed(
                    title="Временная награда.",
                    description=f"{interaction.user.mention}, вы забрали свои 50 <a:coins:1350287791254274078> Возвращайтесь <t:{next_claim_time2}:R>.",
                    color=discord.Color.green()
                    )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)
        if time_passed >= 43200:  # 12 часов в секундах
            self.db.update_balance(str(interaction.user.id), 10000, "+")
            self.db.update_claim_time(str(interaction.user.id))
            await interaction.response.send_message(embed=embed)
        else:
            remaining_time = 43200 - time_passed
            next_claim_time = current_time + remaining_time
            embed.description = f"{interaction.user.mention}, вы не можете забрать награду. Возвращайтесь <t:{next_claim_time}:R>."
            embed.color = discord.Color.red()
            await interaction.response.send_message(embed=embed)    



    # Команда для перевода монет другому пользователю
    @app_commands.command(name="give", description="Перевести монеты другому пользователю.")
    async def command_give(self, interaction: Interaction, target: User, amount: app_commands.Range[int, 10]):
        # Объединенная проверка на перевод самому себе и ботам
        if target.id == interaction.user.id or target.bot:
            error_msg = "Вы не можете перевести монеты самому себе!" if target.id == interaction.user.id else "Вы не можете перевести монеты боту!"
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка!",
                description=error_msg,
                colour=discord.Colour.red()
            ), ephemeral=True)
            return

        user_data = self.db.get_user(str(interaction.user.id))
        target_data = self.db.get_user(str(target.id))
        user_avatar = interaction.user.avatar

        # Создаем класс для кнопок
        class TransferView(discord.ui.View):
            def __init__(self, db):
                super().__init__(timeout=180)  # 3 минуты
                self.db = db

            @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.green)
            async def confirm_callback(self,button_interaction: Interaction,button: discord.ui.Button):
                # Остальной код confirm_callback без изменений
                if interaction.user.id != button_interaction.user.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="Вы не можете подтвердить перевод за другого пользователя.",
                        colour=discord.Colour.red()),ephemeral=True)
                    return
                if user_data['balance'] >= amount:
                    embed = discord.Embed(
                        title="Успешно!",
                        description=f"Вы успешно перевели пользователю {target.mention} {amount} монет. Комиссия 10% ({int(amount*0.1)} монет) удержана.",
                        color=discord.Color.green()
                    )
                    if user_avatar is not None:
                        embed.set_thumbnail(url=user_avatar.url)
                    self.db.update_balance(str(interaction.user.id), amount, "-")
                    self.db.update_balance(str(target.id), int(amount*0.9), "+")
                    await button_interaction.response.edit_message(embed=embed,view=None)
                else:   
                    await button_interaction.response.edit_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="У вас недостаточно монет для перевода.",
                        colour=discord.Colour.red()),view=None)

            @discord.ui.button(label="Отмена", style=discord.ButtonStyle.red)
            async def cancel_callback(self,button_interaction:Interaction,button: discord.ui.Button, ):
                # Остальной код cancel_callback без изменений
                if interaction.user.id != button_interaction.user.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="Вы не можете отменить действие за другого пользователя.",
                        colour=discord.Colour.red()),ephemeral=True)
                    return
                
                await button_interaction.response.edit_message(embed=discord.Embed(
                    title="Отменено!",
                    description=f"Перевод пользователю {target.mention} отменен.",
                    colour=discord.Colour.red()),view=None)

        view = TransferView(self.db)
        embed = discord.Embed(
            title="Подтверждение перевода.",
            description=f"{interaction.user.mention}, вы уверены что хотите передать {int(amount*0.9)} <a:coins:1350287791254274078> \nвключая комиссию 10% пользователю {target.mention}?",
            color=discord.Color.green()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)
        await interaction.response.send_message(embed=embed, view=view)

    # Команда для дуэли на монеты с другим пользователем
    @app_commands.command(name="duel", description="Дуэль на монеты с другим пользователем.")
    async def command_duel(self, interaction: Interaction, target: User, amount: app_commands.Range[int, 10]):
        if target.bot:
            await interaction.response.send_message(embed=discord.Embed(
                title="Дуэль",
                description="Вы не можете дуэлировать с ботом.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return
        
        if interaction.user.id == target.id:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка!",
                description="Вы не можете дуэлировать самим с собой.",
                colour=discord.Colour.red()
            ), ephemeral=True)
            return
        
        user_data = self.db.get_user(str(interaction.user.id))
        target_data = self.db.get_user(str(target.id))

        if user_data['balance']<amount:
            await interaction.response.send_message(embed=discord.Embed(
                title="Дуэль",
                description="У вас недостаточно монет для отправки дуэли.",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        class DuelView(discord.ui.View):
            def __init__(self, db):
                super().__init__(timeout=180)
                self.db = db

            @discord.ui.button(label="Подтвердить",style=discord.ButtonStyle.green)
            async def confirm_callback(self, button_interaction: Interaction, button: discord.ui.Button):
                # Если запрос подтверждает не тот пользователь, которому была отправлена дуэль
                if button_interaction.user.id != target.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="Вы не можете подтвердить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                # Если у пользователя недостаточно монет на балансе
                if button_interaction.user.id == target.id and target_data['balance'] < amount:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="У вас недостаточно монет для подтверждения запроса.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                
                embed_gif = discord.Embed(
                    title="Дуэль началась!",
                    description=f"Дуэль между {interaction.user.mention} и {target.mention} началась!",
                    colour=discord.Colour.blue()
                )

                embed_gif.set_image(url="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYm03OWhqOXVrMDBodXoweWJlY3I2a2Y4YzhjajJ3cTlxNjAxbnFlayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lafkzELQ632WBXExsh/giphy.gif")

                await button_interaction.response.edit_message(embed=embed_gif,view=None)

                await asyncio.sleep(5)

                winner_id = random.choice([user_data['user_id'], target_data['user_id']])
                winner = interaction.guild.get_member(winner_id)
                loser = interaction.guild.get_member(user_data['user_id'] if winner_id == target_data['user_id'] else target_data['user_id'])
                
                self.db.update_balance(str(winner_id), int(amount*0.9), "+")
                self.db.update_balance(str(loser.id), amount, "-")
                
                embed = discord.Embed(
                    title="Дуэль завершена!",
                    description=f"{winner.mention} выиграл дуэль и получил {int(amount*0.9)} <a:coins:1350287791254274078>!",
                    colour=discord.Colour.green())
                
                if winner.avatar is not None:
                    embed.set_thumbnail(url=winner.avatar.url)

                await button_interaction.followup.edit_message(message_id=button_interaction.message.id,embed=embed,view=None)
            
            @discord.ui.button(label="Отменить",style=discord.ButtonStyle.red)
            async def cancel_callback(self, button_interaction: Interaction, button: discord.ui.Button):
                # Если запрос подтверждает не тот пользователь, которому была отправлена дуэль
                if button_interaction.user.id != target.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="Вы не можете отменить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral = True)
                    return
                
                embed = discord.Embed(
                    title="Отмена дуэли.",
                    description=f"{interaction.user.mention}, пользователь {target.mention} отменил дуэль.",
                    colour=discord.Colour.red()
                )

                if interaction.user.avatar is not None:
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                await button_interaction.response.edit_message(embed=embed,view=None)

        view = DuelView(self.db)
        embed = discord.Embed(
            title="Дуэль.",
            description=f"{target.mention}, пользователь {interaction.user.mention} отправил вам запрос на дуэль суммой {amount} <a:coins:1350287791254274078>!",
            colour=discord.Colour.blue()
        )
        if interaction.user.avatar is not None:
            embed.set_thumbnail(url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed,view=view)

        #@app_commands.command(name="casino",description="Испытайте свою удачу в рулетке.")
        #@app_commands.describe

async def setup(bot):
    await bot.add_cog(Economy(bot))
