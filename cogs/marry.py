import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

class Marry(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="marry",description="Предложение руки и сердца.")
    async def command_marry(self, interaction: Interaction, target: User = None):
        if target.id == interaction.user.id:
            await interaction.response.send_message(embed=discord.Embed(
                title="Заключение брака",
                description="Вы не можете отправить запрос на заключение брака самому себе.",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target is None:
            await interaction.response.send_message(embed=discord.Embed(
                title="Заключение брака",
                description="Вы должны выбрать пользователя с которым хотите заключить брак.",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        if target.bot:
            await interaction.response.send_message(embed=discord.Embed(
                title="Заключение брака",
                description="Вы не можете отправить запрос на заключение брака боту.",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return
        
        
        user_data = self.db.get_user(str(interaction.user.id))
        target_data = self.db.get_user(str(target.id))
        user_avatar = interaction.user.avatar

        if user_data['balance']<300:
            await interaction.response.send_message(embed=discord.Embed(
                title="Заключение брака",
                description="На вашем счете недостаточно средств для заключения брака. Цена заключения брака: 300<a:coins:1350287791254274078>",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return

        if target_data['married_with'] != 0:
            await interaction.response.send_message(embed=discord.Embed(
                    title="Заключение брака",
                    description="Данный пользователь уже помолвлен с другим пользователем.",
                    colour=discord.Colour.red()
                ),ephemeral=True)
            return

        class MarryView(discord.ui.View):
            def __init__(self,db):
                super().__init__(timeout=120)
                self.db=db
            
            @discord.ui.button(label="Подтвердить",style=discord.ButtonStyle.green)
            async def confirm_callback(self,button_interaction: Interaction,button = discord.ui.Button):
                if button_interaction.user.id is not target.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Заключение брака",
                        description="Вы не можете подтвердить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                
                self.db.update_married_with(str(interaction.user.id),str(target.id))
                self.db.update_married_with(str(target.id),str(interaction.user.id))
                self.db.update_balance(str(interaction.user.id),300,"-")
                
                embed = discord.Embed(
                    title="Заключение брака",
                    description=f"🎉 Поздравляем {interaction.user.mention} и {target.mention} с официальной свадьбой на сервере Angry Birds!\n💍🐦 Пусть ваша виртуальная любовь будет такой же прочной, как крепость свиней, и такой же яркой, как перья Редда! ❤️🔥",
                    colour=discord.Colour.red()
                )

                embed.set_image(url="https://i.pinimg.com/originals/d0/62/ec/d062ec37ca051f23d670f6e6cdcbbd67.gif")
                await button_interaction.response.edit_message(embed=embed,view=None)

            @discord.ui.button(label="Отменить",style=discord.ButtonStyle.red)
            async def cancel_callback(self, button_interaction: Interaction, button: discord.ui.Button):
                if button_interaction.user.id == interaction.user.id:
                    await button_interaction.response.edit_message(embed=discord.Embed(
                        title="Заключение брака",
                        description=f"{interaction.user.mention}, вы отменили своё предложение.",
                        colour=discord.Colour.red()
                    ),view=None)
                    return
                
                if button_interaction.user.id != target.user.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Заключение брака",
                        description="Вы не можете отменить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ))
                    return

                embed = discord.Embed(
                    title="Заключение брака",
                    description=f"{interaction.user.mention}, мы сожалеем, но пользователь отклонил Ваше предложение на заключение брака.",
                    colour=discord.Colour.red()
                    )

                if user_avatar is not None:
                    embed.set_thumbnail(url=user_avatar.url)
                await button_interaction.response.edit_message(embed=embed,view=None)

        view = MarryView(self.db)
        embed = discord.Embed(
            title="Заключение брака",
            description=f"{target.mention}, пользователь {interaction.user.mention} предлагает вам заключить с ним брак. Стоимость услуги 300<a:coins:1350287791254274078>(монеты взымаются с отправителя)",
            colour=discord.Colour.purple()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)

        await interaction.response.send_message(embed=embed,view=view)
    
    @app_commands.command(name="divorce",description="Расторгнуть брак.")
    async def command_divorce(self,interaction: Interaction):
        user_data = self.db.get_user(str(interaction.user.id))
        user_avatar = interaction.user.avatar
        user_married_with = interaction.guild.get_member(int(user_data['married_with']))

        if user_data['married_with'] == 0:
            await interaction.response.send_message(embed=discord.Embed(
                title="Расторжение брака.",
                description="Вы не находитесь в браке.",
                colour=discord.Colour.blue()
            ),ephemeral=True)
            return
        
        if user_data['balance']<600:
            await interaction.response.send_message(embed=discord.Embed(
                title="Расторжение брака",
                description="У вас недостаточно монет для расторжения брака.",
                colour=discord.Colour.blue()
            ),ephemeral=True)
            return
        
        class DivorceView(discord.ui.View):
            def __init__(self,db):
                super().__init__(timeout=120)
                self.db=db
            
            @discord.ui.button(label="Подтвердить",style=discord.ButtonStyle.green)
            async def confirm_callback(self,button_interaction: Interaction, button: discord.ui.Button):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Расторжение брака",
                        description="Вы не можете подтвердить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                
                user_married_with_data = self.db.get_user(str(user_data["married_with"]))
                user_married_with = interaction.guild.get_member(int(user_data['married_with']))

                self.db.update_married_with(str(user_data['user_id']),"0")
                self.db.update_married_with(str(user_married_with_data['user_id']),"0")
                self.db.update_balance(str(interaction.user.id),600,"-")

                embed = discord.Embed(
                    title="Расторжение брака",
                    description=f"{interaction.user.mention}, ваш брак с пользователем {user_married_with.mention} был расторгнут.",
                    colour=discord.Colour.red()
                )

                if user_avatar is not None:
                    embed.set_thumbnail(url=user_avatar.url)
                await button_interaction.response.edit_message(embed=embed,view=None)

            @discord.ui.button(label="Отменить",style=discord.ButtonStyle.red)
            async def cancell_callback(self,button_interaction: Interaction, button: discord.ui.Button):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Расторжение брака",
                        description="Вы не можете отменить действие за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                await button_interaction.response.edit_message(embed=discord.Embed(
                    title="Расторжение брака",
                    description=f"{interaction.user.mention}, вы отменили запрос на расторжение брака.",
                    color=discord.Colour.red()
                ),view=None)

        view = DivorceView(self.db)
        embed = discord.Embed(
            title="Расторжение брака",
            description=f"{interaction.user.mention}, вы уверены что хотите расторгнуть брак с пользователем {user_married_with.mention}? Стоимость услуги 600<a:coins:1350287791254274078>",
            colour=discord.Colour.blue()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url = user_avatar.url)
        await interaction.response.send_message(embed=embed,view=view)
                

async def setup(bot):
    await bot.add_cog(Marry(bot))