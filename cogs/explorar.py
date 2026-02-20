import discord
from discord import app_commands
from discord.ext import commands
from views.explorar_view import ExplorarView
from views.location_view import LocationView
from icons.emojis import EMOJIS
from utils.database import is_user_traveling, get_travel_state, clear_travel_state, salvar_inventarios, is_command_under_maintenance
from utils.models import player_data
from datetime import datetime

class Explorar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="explorar", description="Inicia uma expedição")
    async def explorar(self, interaction: discord.Interaction):
        if is_command_under_maintenance("explorar"):
            embed = discord.Embed(
                title="🔧 Comando em Manutenção",
                description="O comando /explorar está temporariamente indisponível devido a manutenção.\n\nVolte em breve!",
                color=0x81919E
            )
            embed.set_thumbnail(url="https://minecraft.wiki/images/Clockwise_Gear_%28N%29.gif?d648f")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="🌍 Explorar",
                description="Escolha um destino para explorar:",
                color=0x00AA00
            )
            view = ExplorarView()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Explorar(bot))
