import discord
from discord import app_commands
from discord.ext import commands
from utils.database import get_moedas, get_blocos_quebrados, get_xp_sqlite, adicionar_item
from icons.emojis_icones import EMOJIS_ICONES
from icons.emojis_picaretas import EMOJIS_PICARETAS
from views.itens_crafting import ITENS_CRAFTING

OWNER_ID = 1324198892648009760

class VerJogador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ver_jogador", description="Ver informações detalhadas de um jogador (apenas dono)")
    @app_commands.describe(jogador="Jogador para ver as informações")
    async def ver_jogador(self, interaction: discord.Interaction, jogador: discord.Member):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
            return

        user_id = str(jogador.id)
        moedas = get_moedas(user_id)
        blocos = get_blocos_quebrados(user_id)
        xp = get_xp_sqlite(user_id)

        embed = discord.Embed(
            title=f"{EMOJIS_ICONES['amigos']} Informações de {jogador.name}",
            color=0x9C59B6
        )
        embed.add_field(name=f"{EMOJIS_ICONES['steve']} Nome", value=jogador.name, inline=True)
        embed.add_field(name=f"{EMOJIS_ICONES['online']} ID", value=jogador.id, inline=True)
        embed.add_field(name=f"{EMOJIS_ICONES['minecoin']} Minecoins", value=moedas, inline=True)
        embed.add_field(name=f"{EMOJIS_PICARETAS['picareta de ferro']} Blocos Quebrados", value=blocos, inline=True)
        embed.add_field(name="⭐ XP", value=xp, inline=True)
        embed.set_thumbnail(url=jogador.avatar.url if jogador.avatar else jogador.default_avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="dar_itens_todos", description="Dar todos os itens craftáveis ao dono")
    async def dar_itens_todos(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
            return

        user_id = str(OWNER_ID)
        added_items = 0

        for categoria, itens in ITENS_CRAFTING.items():
            for item in itens:
                nome = item["nome"]
                adicionar_item(user_id, nome, 1)
                added_items += 1

        embed = discord.Embed(
            title="✅ Itens Adicionados",
            description=f"Adicionados {added_items} itens ao seu inventário!",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerJogador(bot))
