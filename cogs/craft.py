import discord
from discord import app_commands
from discord.ext import commands
from utils.database import carregar_dados
from views.view_craft import CategoriaDropdownView
from icons.emojis import EMOJIS

class Craft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="craft", description=f"Sistema de Criação")
    async def craft(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        dados = carregar_dados(user_id)

        inventario = dados.get("inventario", dados)

        campos_ignorados = [
            "bioma_atual", "xp", "nivel", "vida", "fome",
            "plantacao_ativa", "registrado", "animais_disponiveis",
            "recursos_disponiveis"
        ]
        total_itens = sum(v for k, v in inventario.items()
                          if k not in campos_ignorados and isinstance(v, (int, float)))

        embed = discord.Embed(
            title=f"{EMOJIS['crafting']} Sistema de Criação",
            description=f"Escolha uma categoria para ver os itens disponíveis.",
            color=discord.Color.orange()
        )
        embed.set_image(url="https://tse1.mm.bing.net/th/id/OIP.jSCOpWbI0rZ9gB95hOdUXAAAAA?pid=Api&P=0&h=180")
        embed.set_footer(text="Selecione uma categoria.")
        await interaction.response.send_message(embed=embed, view=CategoriaDropdownView(interaction.user.id), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Craft(bot))
    print("✅ Cog craft.py carregado com sucesso!")
    try:
        GUILD_ID = 1390373570559086692
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos do craft: {e}")
