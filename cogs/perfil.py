import discord
from discord.ext import commands
from discord import app_commands
from views.botoesperfil import BotoesPerfil
from views.view_status import StatusView
from utils.database import inventarios, get_status, get_xp_progresso_atual, calcular_nivel_por_xp, get_moedas, get_saldo
from icons.emojis_minerios import EMOJIS_MINERIOS
from icons.emojis import EMOJIS
from utils.minecraft_time import get_minecraft_time, is_night
from datetime import datetime
import time
from utils.minecraft_time import get_time_offset

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perfil", description="Veja seu perfil")
    async def perfil(self, interaction: discord.Interaction):
        user_inv = inventarios.get(str(interaction.user.id), {})
        
        embed = discord.Embed(
            title=f"{EMOJIS.get('villagerfazendeiro', '👨‍🌾')} Perfil de {interaction.user.name}",
            color=discord.Color.green()
        )
        
        plantacao = user_inv.get("plantacao_ativa", None)
        
        if plantacao:
            tempo_atual = datetime.now().timestamp()
            tempo_restante = plantacao["tempo_colheita"] - tempo_atual
            
            tipo = plantacao["tipo"]
            emoji = {"trigo": EMOJIS.get('trigo', '🌾'), "cenoura": "🥕", "batata": "🥔", "beterraba": "🍠"}.get(tipo, "🌱")
            
            if tempo_restante <= 0:
                status_plantacao = f"✅ **{emoji} {tipo.title()} PRONTO PARA COLHER!**"
                embed.add_field(name=f"{EMOJIS.get('trigo', '🌾')} Plantação", value=status_plantacao, inline=False)
            else:
                horas = int(tempo_restante // 3600)
                minutos = int((tempo_restante % 3600) // 60)
                segundos = int(tempo_restante % 60)
                
                if horas > 0:
                    tempo_texto = f"{horas}h {minutos}m"
                else:
                    tempo_texto = f"{minutos}m {segundos}s"
                
                status_plantacao = f"🌱 **{emoji} {tipo.title()}** crescendo...\n⏰ {tempo_texto} restantes"
                embed.add_field(name=f"{EMOJIS.get('trigo', '🌾')} Plantação Ativa", value=status_plantacao, inline=False)
        else:
            embed.add_field(name=f"{EMOJIS.get('trigo', '🌾')} Plantação", value="Nenhuma plantação ativa", inline=False)

        embed.set_thumbnail(url="https://minecraft.wiki/images/Steve_%28classic%29_JE6.png?format=original")

        embed.set_image(url="https://www.kolpaper.com/wp-content/uploads/2020/10/Minecraft-Inventory-Wallpaper-2.jpg")
        
        embed.set_footer(text="ExploraCraft - Seu perfil de aventureiro")

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            view=BotoesPerfil(interaction.user.id)
        )

    @app_commands.command(name="status", description="Veja seu status de vida, fome e XP")
    async def status(self, interaction: discord.Interaction):
        """Show player's status with health, hunger, and XP bars"""
        view = StatusView(str(interaction.user.id))
        await view.show_status(interaction)

async def setup(bot):
    await bot.add_cog(Perfil(bot))
