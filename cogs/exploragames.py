import discord
from discord import app_commands
from discord.ext import commands
from views.exploragames_view import ExploragamesView
from icons.emojis import EMOJIS

class Exploragames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="exploragames", description="Jogue jogos divertidos inspirados no Minecraft")
    async def exploragames(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 ExploraGames",
            description=f"Escolha um jogo para jogar:\n{EMOJIS.get('TNT', '💣')} Mines, um jogo cheio que minas é cheio de diamantes para resgatar!\n{EMOJIS.get('pedregulho', '🪨')} Pedra, papel é tesoura jogue contra o bot ou contra um amigo.",
            color=0x00AA00
        )
        view = ExploragamesView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Exploragames(bot))
