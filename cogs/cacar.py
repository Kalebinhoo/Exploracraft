import discord
from discord.ext import commands
from discord import app_commands
import random
from views.view_cacar import BotoesCacar
from utils.database import tentativas_cacar, inventarios, salvar_inventarios, get_inventario, get_inventario_sqlite
from utils.animais import animais
from icons.emojis import EMOJIS

class Cacar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def verificar_espada(self, user_id):
        """Verifica se o jogador tem qualquer tipo de espada"""
        user_inv_db = get_inventario_sqlite(str(user_id))
        user_inv_json = inventarios.get(str(user_id), {})
        user_inv = {**user_inv_db, **user_inv_json}
        espadas_permitidas = [
            "Espada de Madeira", "espada de madeira",
            "Espada de Pedra", "espada de pedra",
            "Espada de Ferro", "espada de ferro",
            "Espada de Ouro", "espada de ouro",
            "Espada de Diamante", "espada de diamante"
        ]

        def get_quantity(item):
            qty = user_inv.get(item, 0)
            if isinstance(qty, list):
                return sum(qty)
            else:
                return qty

        return any(get_quantity(espada) > 0 for espada in espadas_permitidas)

    @app_commands.command(name="caçar", description="Procure por um animal na floresta")
    async def cacar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        if not self.verificar_espada(user_id):
            embed = discord.Embed(
                title="⚠️ Espada necessária",
                description="Você precisa de uma espada para caçar!\nFaça uma com `/craft` primeiro.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tentativas = tentativas_cacar.get(user_id, 0)

        if tentativas >= 10:
            embed = discord.Embed(
                title=f"{EMOJIS['barreira']} Limite de tentativas",
                description="Você não encontrou nenhum animal após 10 tentativas.\nUse `/pararcaçar` para resetar.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tentativas_cacar[user_id] = tentativas + 1
        encontrou = random.random() < 0.4

        if encontrou:
            animal = random.choice(list(animais.keys()))
            dados = animais[animal]

            embed = discord.Embed(
                title=f"🐾 Você encontrou uma {animal}!",
                description="Escolha uma ação abaixo:",
                color=0x88c999
            )
            embed.set_image(url=dados["imagem"])
            embed.set_footer(text="Use os botões para interagir com o animal")

            view = BotoesCacar(animal, interaction.user)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
            tentativas_cacar.pop(user_id, None)
        else:
            embed = discord.Embed(
                title=f"{EMOJIS.get('lupa', '🔎')} Nenhum animal encontrado",
                description=f"Tentativa {tentativas + 1}/10\nContinue tentando!",
                color=0xAAAAAA
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Cacar(bot))
