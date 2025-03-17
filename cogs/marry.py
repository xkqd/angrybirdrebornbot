import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

class Marry(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="marry",description="Женитьба.")
    async def command_marry(self, interaction: Interaction, target: User = None):
        if target is None:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка!",
                description="Вы должны выбрать пользователя с которым хотите пожениться.",
                colour=discord.Colour.red()
            ),ephemeral=True)
            return
        user_data = self.db.get_user(str(interaction.user.id))
        target = self.db.get_user(str(target.id))

        class MarryView(discord.ui.View):
            def __init__(self,db):
                super().__init__(timeout=120)
                self.db=db
            
            @discord.ui.button(label="Подтвердить",style=discord.ButtonStyle.blurple)
            async def confirm_callback(self,button_interaction: Interaction,button = discord.ui.Button):
                if button_interaction.user.id is not target.id:
                    await button_interaction.response.send_message(embed=discord.Embed(
                        title="Ошибка!",
                        description="Вы не можете подвердить запрос за другого пользователя.",
                        colour=discord.Colour.red()
                    ),ephemeral=True)
                    return
                

                


async def setup(bot):
    await bot.add_cog(Marry(bot))