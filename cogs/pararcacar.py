from discord.ext import commands
from discord import app_commands
import discord

from utils.database import tentativas_cacar

class PararCacar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pararcaçar", description="Desiste da caçada e reseta tentativas")
    async def pararcacar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in tentativas_cacar:
            tentativas_cacar.pop(user_id)
            await interaction.response.send_message("🛑 Você desistiu da caçada. Tentativas foram resetadas.", ephemeral=True)
        else:
            await interaction.response.send_message("❗ Você não está caçando no momento.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PararCacar(bot))
