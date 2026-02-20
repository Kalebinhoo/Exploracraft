import discord
import random
from utils.database import inventarios, salvar_inventarios, adicionar_xp, possui_item, remover_item
from icons.emojis import EMOJIS

class BotoesMineracao(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="⛏️ Minerar", style=discord.ButtonStyle.primary)
    async def minerar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.get(str(interaction.user.id), {})

        pickaxe_hierarchy = ["Picareta de Diamante", "Picareta de Ferro", "Picareta de Ouro", "Picareta de Pedra", "Picareta de Madeira"]
        best_pickaxe = None
        for p in pickaxe_hierarchy:
            if possui_item(interaction.user.id, p):
                best_pickaxe = p
                break

        if not best_pickaxe:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Sua picareta quebrou! Crie uma nova.", ephemeral=True)
            return

        if best_pickaxe == "Picareta de Madeira":
            recursos = {
                "pedra": {"chance": 45, "min": 2, "max": 4, "emoji": "🪨", "xp": 1},
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": EMOJIS.get('carvao', '⚫'), "xp": 2}
            }
        elif best_pickaxe == "Picareta de Pedra":
            recursos = {
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": EMOJIS.get('carvao', '⚫'), "xp": 2},
                "ferro": {"chance": 15, "min": 1, "max": 2, "emoji": "🔩", "xp": 5}
            }
        else:
            recursos = {
                "pedra": {"chance": 45, "min": 2, "max": 4, "emoji": "🪨", "xp": 1},
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": "<:carvao:1408877082674728980>", "xp": 2},
                "ferro": {"chance": 15, "min": 1, "max": 2, "emoji": "🔩", "xp": 5},
                "ouro": {"chance": 8, "min": 1, "max": 2, "emoji": "🟡", "xp": 8},
                "diamante": {"chance": 2, "min": 1, "max": 1, "emoji": "💎", "xp": 15}
            }

        rand = random.randint(1, 100)
        recurso_encontrado = None
        chance_acumulada = 0

        for recurso, dados in recursos.items():
            chance_acumulada += dados["chance"]
            if rand <= chance_acumulada:
                recurso_encontrado = recurso
                break

        if not recurso_encontrado:
            embed = discord.Embed(
                title="⛏️ Mineração",
                description="🕳️ Você cavou mas não encontrou nada útil...\nTente novamente!",
                color=discord.Color.dark_gray()
            )
            embed.set_image(url="https://minecraft.wiki/images/1/1d/Stone.png")
            await interaction.response.edit_message(embed=embed, view=self)
            return

        dados_recurso = recursos[recurso_encontrado]
        quantidade = random.randint(dados_recurso["min"], dados_recurso["max"])
        
        user_inv[recurso_encontrado] = user_inv.get(recurso_encontrado, 0) + quantidade
        
        xp_info = adicionar_xp(interaction.user.id, dados_recurso["xp"] * quantidade)

        chance_quebrar = 5 if best_pickaxe == "Picareta de Madeira" else 2
        picareta_quebrou = random.randint(1, 100) <= chance_quebrar

        if picareta_quebrou:
            remover_item(interaction.user.id, best_pickaxe, 1)
            picareta_tipo = best_pickaxe

        salvar_inventarios()

        has_pickaxe_left = possui_item(interaction.user.id, "picareta")

        embed = discord.Embed(
            title="⛏️ Mineração Bem-sucedida!",
            color=discord.Color.green()
        )

        imagens = {
            "pedra": "https://minecraft.wiki/images/1/1d/Stone.png",
            "Carvão": "https://minecraft.wiki/images/a/a6/Coal_Ore_JE4_BE3.png",
            "ferro": "https://minecraft.wiki/images/f/f7/Iron_Ore_JE6_BE4.png",
            "ouro": "https://minecraft.wiki/images/0/01/Gold_Ore_JE6_BE4.png",
            "diamante": "https://minecraft.wiki/images/5/56/Diamond_Ore_JE6_BE4.png"
        }

        embed.set_image(url=imagens.get(recurso_encontrado, imagens["pedra"]))

        resultado_texto = f"{dados_recurso['emoji']} **{recurso_encontrado.title()}**: +{quantidade}\n⭐ **XP**: +{xp_info['xp_ganho']}"

        if xp_info['subiu_nivel']:
            resultado_texto += f"\n🎉 **Level Up!** Nível {xp_info['nivel_atual']}"

        if picareta_quebrou:
            resultado_texto += f"\n💥 Sua {picareta_tipo} quebrou!"

        embed.add_field(name="📦 Recursos Encontrados", value=resultado_texto, inline=False)
        embed.set_footer(text="Continue minerando para encontrar mais recursos!")

        if has_pickaxe_left:
            view_result = MineracaoResultView(self.user_id)
        else:
            view_result = None

        await interaction.response.edit_message(embed=embed, view=view_result)

    @discord.ui.button(label="🚪 Sair da Caverna", style=discord.ButtonStyle.secondary)
    async def sair(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🚪 Saindo da Caverna",
            description="Você saiu da caverna com segurança!\nUse `/minerar` novamente quando quiser voltar.",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://minecraft.wiki/images/6/6a/Plains.png")

        await interaction.response.edit_message(embed=embed, view=None)

class MineracaoResultView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="Minerar Novamente", style=discord.ButtonStyle.primary, emoji=EMOJIS.get('picareta de ferro', '⛏️'))
    async def minerar_novamente(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        await interaction.response.defer()

        loading_embed = discord.Embed(
            title=f"{EMOJIS.get('picareta de ferro', '⛏️')} Minerando...",
            description="Aguarde enquanto você minera recursos!",
            color=discord.Color.blue()
        )
        await interaction.edit_original_response(embed=loading_embed, view=None)

        user_inv = inventarios.get(str(interaction.user.id), {})

        pickaxe_hierarchy = ["Picareta de Diamante", "Picareta de Ferro", "Picareta de Ouro", "Picareta de Pedra", "Picareta de Madeira"]
        best_pickaxe = None
        for p in pickaxe_hierarchy:
            if possui_item(interaction.user.id, p):
                best_pickaxe = p
                break

        if not best_pickaxe:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Sua picareta quebrou! Crie uma nova.", ephemeral=True)
            return

        if best_pickaxe == "Picareta de Madeira":
            recursos = {
                "pedra": {"chance": 45, "min": 2, "max": 4, "emoji": "🪨", "xp": 1},
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": EMOJIS.get('carvao', '⚫'), "xp": 2}
            }
        elif best_pickaxe == "Picareta de Pedra":
            recursos = {
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": EMOJIS.get('carvao', '⚫'), "xp": 2},
                "ferro": {"chance": 15, "min": 1, "max": 2, "emoji": "🔩", "xp": 5}
            }
        else:
            recursos = {
                "pedra": {"chance": 45, "min": 2, "max": 4, "emoji": "🪨", "xp": 1},
                "Carvão": {"chance": 25, "min": 1, "max": 3, "emoji": "<:carvao:1408877082674728980>", "xp": 2},
                "ferro": {"chance": 15, "min": 1, "max": 2, "emoji": "🔩", "xp": 5},
                "ouro": {"chance": 8, "min": 1, "max": 2, "emoji": "🟡", "xp": 8},
                "diamante": {"chance": 2, "min": 1, "max": 1, "emoji": "💎", "xp": 15}
            }

        rand = random.randint(1, 100)
        recurso_encontrado = None
        chance_acumulada = 0

        for recurso, dados in recursos.items():
            chance_acumulada += dados["chance"]
            if rand <= chance_acumulada:
                recurso_encontrado = recurso
                break

        if not recurso_encontrado:
            embed = discord.Embed(
                title="⛏️ Mineração",
                description="🕳️ Você cavou mas não encontrou nada útil...\nTente novamente!",
                color=discord.Color.dark_gray()
            )
            embed.set_image(url="https://minecraft.wiki/images/1/1d/Stone.png")
            await interaction.response.send_message(embed=embed, view=BotoesMineracao(self.user_id), ephemeral=True)
            return

        dados_recurso = recursos[recurso_encontrado]
        quantidade = random.randint(dados_recurso["min"], dados_recurso["max"])

        user_inv[recurso_encontrado] = user_inv.get(recurso_encontrado, 0) + quantidade

        xp_info = adicionar_xp(interaction.user.id, dados_recurso["xp"] * quantidade)

        chance_quebrar = 5 if best_pickaxe == "Picareta de Madeira" else 2
        picareta_quebrou = random.randint(1, 100) <= chance_quebrar

        if picareta_quebrou:
            remover_item(interaction.user.id, best_pickaxe, 1)
            picareta_tipo = best_pickaxe

        salvar_inventarios()

        has_pickaxe_left = possui_item(interaction.user.id, "picareta")

        embed = discord.Embed(
            title="⛏️ Mineração Bem-sucedida!",
            color=discord.Color.green()
        )

        imagens = {
            "pedra": "https://minecraft.wiki/images/1/1d/Stone.png",
            "Carvão": "https://minecraft.wiki/images/a/a6/Coal_Ore_JE4_BE3.png",
            "ferro": "https://minecraft.wiki/images/f/f7/Iron_Ore_JE6_BE4.png",
            "ouro": "https://minecraft.wiki/images/0/01/Gold_Ore_JE6_BE4.png",
            "diamante": "https://minecraft.wiki/images/5/56/Diamond_Ore_JE6_BE4.png"
        }

        embed.set_image(url=imagens.get(recurso_encontrado, imagens["pedra"]))

        resultado_texto = f"{dados_recurso['emoji']} **{recurso_encontrado.title()}**: +{quantidade}\n⭐ **XP**: +{xp_info['xp_ganho']}"

        if xp_info['subiu_nivel']:
            resultado_texto += f"\n🎉 **Level Up!** Nível {xp_info['nivel_atual']}"

        if picareta_quebrou:
            resultado_texto += f"\n💥 Sua {picareta_tipo} quebrou!"

        embed.add_field(name="📦 Recursos Encontrados", value=resultado_texto, inline=False)
        embed.set_footer(text="Continue minerando para encontrar mais recursos!")

        if has_pickaxe_left:
            await interaction.edit_original_response(embed=embed, view=MineracaoResultView(self.user_id))
        else:
            await interaction.edit_original_response(embed=embed, view=None)