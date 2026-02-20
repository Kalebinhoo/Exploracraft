import discord
from discord import app_commands
from discord.ext import commands
from utils.database import get_moedas, adicionar_moedas
from icons.emojis_icones import EMOJIS_ICONES
import json
import os
import sqlite3
from contextlib import closing

OWNER_ID = 1324198892648009760

def get_all_balances():
    """Retorna um dicionário com todos os usuários que têm saldo."""
    db_path = 'minecraft.db'
    balances = {}
    with closing(sqlite3.connect(db_path)) as conn:
        c = conn.cursor()
        c.execute('SELECT id, moedas FROM jogadores WHERE moedas > 0')
        rows = c.fetchall()
        for row in rows:
            balances[row[0]] = row[1]
    return balances

def save_balances_to_json():
    """Salva todos os saldos em um arquivo JSON."""
    balances = get_all_balances()
    with open('saldos.json', 'w') as f:
        json.dump(balances, f, indent=4)

class Saldo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="saldo", description="Veja seu saldo de Minecoins")
    async def saldo(self, interaction: discord.Interaction):
        moedas = get_moedas(str(interaction.user.id))

        embed = discord.Embed(
            title=f"{EMOJIS_ICONES['saco']} Seu Saldo",
            description=f"{EMOJIS_ICONES['minecoin']} **Minecoins:** {moedas}",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Caso você perder suas Minecoins/ me avise a quantidade que tinha para mim pode te tranferir!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        save_balances_to_json()

    @app_commands.command(name="adicionar_saldo", description="Adiciona Minecoins a um jogador (apenas dono)")
    @app_commands.describe(
        usuario="Usuário para adicionar saldo",
        quantidade="Quantidade de Minecoins a adicionar"
    )
    async def adicionar_saldo(self, interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
            return

        if quantidade <= 0:
            await interaction.response.send_message("❌ A quantidade deve ser positiva.", ephemeral=True)
            return

        user_id = str(usuario.id)

        adicionar_moedas(user_id, quantidade)

        embed = discord.Embed(
            title="✅ Saldo Adicionado",
            description=f"Adicionado {quantidade} {EMOJIS_ICONES['minecoin']} Minecoins para {usuario.mention}",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            dm_embed = discord.Embed(
                title="💰 Você recebeu Minecoins!",
                description=f"Você recebeu **{quantidade}** {EMOJIS_ICONES['minecoin']} Minecoins.",
                color=discord.Color.green()
            )
            dm_embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            dm_embed.add_field(name="Enviado por", value=f"{interaction.user.name}#{interaction.user.discriminator}", inline=True)
            dm_embed.add_field(name="ID do Remetente", value=str(interaction.user.id), inline=True)
            dm_embed.add_field(name="Valor", value=f"{quantidade} Minecoins", inline=True)
            dm_embed.set_footer(text="Caso tenha dúvidas, contate um administrador.")

            await usuario.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        save_balances_to_json()

async def setup(bot):
    await bot.add_cog(Saldo(bot))
