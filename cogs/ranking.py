import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from typing import Dict, List, Tuple
from icons.emojis import EMOJIS

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def carregar_inventarios(self) -> Dict:
        """Carrega os inventários do arquivo JSON"""
        try:
            with open('inventarios.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def carregar_saldos(self) -> Dict:
        """Carrega os saldos do arquivo JSON"""
        try:
            with open('saldos.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def calcular_ranking_mineracao(self, inventarios: Dict) -> List[Tuple[str, int, str]]:
        """
        Calcula o ranking de mineração baseado nos itens minerados
        Retorna: [(user_id, quantidade_total, nome_principal_item), ...]
        """
        ranking = []

        itens_mineracao = [
            "Pedregulho", "Carvão", "Ferro", "Ouro", "Diamante",
            "Redstone", "Lapis Lazuli", "Esmeralda", "Carvão Mineral"
        ]

        for user_id, dados in inventarios.items():
            if not isinstance(dados, dict):
                continue

            total_minerado = 0
            item_principal = "Pedregulho"
            max_quantidade = 0
            for item, quantidade in dados.items():
                if isinstance(quantidade, list):
                    qty = sum(quantidade)
                elif isinstance(quantidade, int):
                    qty = quantidade
                else:
                    qty = 0

                if qty > 0:
                    for item_mineracao in itens_mineracao:
                        if item_mineracao.lower() in item.lower():
                            total_minerado += qty
                            if qty > max_quantidade:
                                max_quantidade = qty
                                item_principal = item
                            break

            if total_minerado > 0:
                ranking.append((user_id, total_minerado, item_principal))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def calcular_ranking_minecoins(self, saldos: Dict) -> List[Tuple[str, int]]:
        """
        Calcula o ranking de Minecoins
        Retorna: [(user_id, quantidade), ...]
        """
        ranking = []

        for user_id, quantidade in saldos.items():
            if isinstance(quantidade, int) and quantidade > 0:
                ranking.append((user_id, quantidade))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def calcular_ranking_xp(self, inventarios: Dict) -> List[Tuple[str, int]]:
        """
        Calcula o ranking de XP
        Retorna: [(user_id, xp), ...]
        """
        ranking = []

        for user_id, dados in inventarios.items():
            if isinstance(dados, dict):
                xp = dados.get("xp", 0)
                if xp > 0:
                    ranking.append((user_id, xp))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    @app_commands.command(name="ranking", description="Veja os rankings de mineração e Minecoins!")
    async def ranking(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{EMOJIS.get('trofeu', '🏆')} Rankings - ExploraCraft",
            description="Escolha o tipo de ranking que deseja ver:",
            color=0xFFD700
        )
        embed.add_field(
            name=f"{EMOJIS.get('picareta de ferro', '⛏️')} Mineração",
            value="Ranking dos melhores mineradores baseado em itens extraídos",
            inline=True
        )
        embed.add_field(
            name=f"{EMOJIS.get('minecoin', '💰')} Minecoins",
            value="Ranking dos jogadores mais ricos em Minecoins",
            inline=True
        )
        embed.add_field(
            name=f"{EMOJIS.get('experiencia', '<a:experiencia:1410458227652427827>')} XP",
            value="Ranking dos jogadores com mais experiência",
            inline=True
        )
        embed.set_footer(text="Clique em um botão abaixo para ver o ranking!")

        view = RankingView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def criar_embed_ranking(self, ranking_type: str, ranking_data: List, bot) -> discord.Embed:
        if ranking_type == "mineracao":
            title = f"{EMOJIS.get('trofeu', '🏆')} Ranking de Mineração - ExploraCraft"
            description = "<a:medalhadiamante:1417968536810160258> **Top 3 Mineradores do Servidor**\n\nOs melhores mineradores baseados em itens extraídos!"
            emoji_item = EMOJIS.get('picareta de ferro', '⛏️')
            footer = "💡 Mine mais para subir no ranking! | Sistema ExploraCraft"
        elif ranking_type == "minecoins":
            title = f"{EMOJIS.get('trofeu', '🏆')} Ranking de Minecoins - ExploraCraft"
            description = "<a:medalhadiamante:1417968536810160258> **Top 3 Mais Ricos do Servidor**\n\nOs jogadores com mais Minecoins!"
            emoji_item = "Minecoins"
            footer = "💡 Ganhe mais Minecoins para subir no ranking! | Sistema ExploraCraft"
        else:
            title = f"{EMOJIS.get('trofeu', '🏆')} Ranking de XP - ExploraCraft"
            description = "<a:medalhadiamante:1417968536810160258> **Top 3 Jogadores com Mais XP**\n\nOs jogadores com mais experiência!"
            emoji_item = EMOJIS.get('experiencia', '<a:experiencia:1410458227652427827>')
            footer = "💡 Ganhe mais XP para subir no ranking! | Sistema ExploraCraft"

        embed = discord.Embed(
            title=title,
            description=description,
            color=0xFFD700
        )

        for i, data in enumerate(ranking_data[:3], 1):
            if ranking_type == "mineracao":
                user_id, quantidade, item_principal = data
                value = f"{emoji_item} **{quantidade}** itens minerados\n{EMOJIS.get('pedregulho', '💎')} Item principal: **{item_principal}**"
            elif ranking_type == "minecoins":
                user_id, quantidade = data
                value = f"**{quantidade}** {emoji_item}"
            else:
                user_id, quantidade = data
                value = f"{emoji_item} **{quantidade}** XP"

            user = bot.get_user(int(user_id))
            if not user:
                try:
                    user = await bot.fetch_user(int(user_id))
                except:
                    user = None
            nome_usuario = user.name if user else f"Usuário {user_id}"

            medalhas = {
                1: "<a:medalhadiamante:1417968536810160258>",
                2: "<a:medalhaouro:1417968540203618395>",
                3: "<a:medalhacobre:1417968538387222730>"
            }

            emoji_pos = medalhas.get(i, f"{i}.")
            embed.add_field(
                name=f"{emoji_pos} {nome_usuario}",
                value=value,
                inline=False
            )

        total_jogadores = len(ranking_data)
        if ranking_type == "mineracao":
            total_itens = sum(r[1] for r in ranking_data)
            stats_value = f"{EMOJIS.get('amigos', '👥')} **{total_jogadores}** mineradores ativos\n{emoji_item} **{total_itens}** itens minerados no total"
        elif ranking_type == "minecoins":
            total_coins = sum(r[1] for r in ranking_data)
            stats_value = f"{EMOJIS.get('amigos', '👥')} **{total_jogadores}** jogadores com Minecoins\n**{total_coins}** {emoji_item} no total"
        else:
            total_xp = sum(r[1] for r in ranking_data)
            stats_value = f"{EMOJIS.get('amigos', '👥')} **{total_jogadores}** jogadores com XP\n{emoji_item} **{total_xp}** XP no total"

        embed.add_field(
            name=f"{EMOJIS.get('online', '📊')} Estatísticas Gerais",
            value=stats_value,
            inline=False
        )

        embed.set_footer(text=footer)
        return embed

class MiningRankingButton(Button):
    def __init__(self):
        super().__init__(label="Mineração", emoji=EMOJIS.get('picareta de ferro', '⛏️'), style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cog = interaction.client.get_cog('Ranking')
        if not cog:
            return

        inventarios = cog.carregar_inventarios()
        ranking_data = cog.calcular_ranking_mineracao(inventarios)

        if not ranking_data:
            embed = discord.Embed(
                title=f"{EMOJIS.get('trofeu', '🏆')} Ranking de Mineração",
                description=f"{EMOJIS.get('c_negativo', '❌')} Nenhum jogador minerou ainda!",
                color=discord.Color.yellow()
            )
        else:
            embed = await cog.criar_embed_ranking("mineracao", ranking_data, interaction.client)

        await interaction.response.edit_message(embed=embed, view=None)

class MinecoinsRankingButton(Button):
    def __init__(self):
        super().__init__(label="Minecoins", emoji=EMOJIS.get('minecoin', '💰'), style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cog = interaction.client.get_cog('Ranking')
        if not cog:
            return

        saldos = cog.carregar_saldos()
        ranking_data = cog.calcular_ranking_minecoins(saldos)

        if not ranking_data:
            embed = discord.Embed(
                title=f"{EMOJIS.get('trofeu', '🏆')} Ranking de Minecoins",
                description=f"{EMOJIS.get('c_negativo', '❌')} Nenhum jogador tem Minecoins ainda!",
                color=discord.Color.yellow()
            )
        else:
            embed = await cog.criar_embed_ranking("minecoins", ranking_data, interaction.client)

        await interaction.response.edit_message(embed=embed, view=None)

class XPRankingButton(Button):
    def __init__(self):
        super().__init__(label="XP", emoji=EMOJIS.get('experiencia', '<a:experiencia:1410458227652427827>'), style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cog = interaction.client.get_cog('Ranking')
        if not cog:
            return

        inventarios = cog.carregar_inventarios()
        ranking_data = cog.calcular_ranking_xp(inventarios)

        if not ranking_data:
            embed = discord.Embed(
                title=f"{EMOJIS.get('trofeu', '🏆')} Ranking de XP",
                description=f"{EMOJIS.get('c_negativo', '❌')} Nenhum jogador tem XP ainda!",
                color=discord.Color.yellow()
            )
        else:
            embed = await cog.criar_embed_ranking("xp", ranking_data, interaction.client)

        await interaction.response.edit_message(embed=embed, view=None)

class RankingView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MiningRankingButton())
        self.add_item(MinecoinsRankingButton())
        self.add_item(XPRankingButton())

async def setup(bot):
    await bot.add_cog(Ranking(bot))
