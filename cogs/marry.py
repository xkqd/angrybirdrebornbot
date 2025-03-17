import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

class Marry(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="marry",description="Женитьба.")
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
                        description="Вы не можете принять запрос за другого пользователя.",
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
                
                if user_avatar is not None:
                    embed.set_thumbnail(url=user_avatar.url)

                embed.set_image(url="https://i.pinimg.com/originals/d0/62/ec/d062ec37ca051f23d670f6e6cdcbbd67.gif")
                await button_interaction.response.edit_message(embed=embed,view=None)

            @discord.ui.button(label="Отменить",style=discord.ButtonStyle.red)
            async def cancel_callback(self, button_interaction: Interaction, button: discord.ui.Button):
                if button_interaction.user.id == interaction.user.id:
                    await button_interaction.response.edit_message(embed=discord.Embed(
                        title="Заключение брака",
                        description=f"{interaction.user.mention}, вы отменили своё предложение.",
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
            description=f"{target.mention}, пользователь {interaction.user.mention} предлагает вам заключить с ним брак.",
            colour=discord.Colour.purple()
        )
        if user_avatar is not None:
            embed.set_thumbnail(url=user_avatar.url)

        await interaction.response.send_message(embed=embed,view=view)

async def setup(bot):
    await bot.add_cog(Marry(bot))