from discord.ui import Select, View
import discord
import json
import os
from icons.emojis import EMOJIS

class LojaDropdownView(View):
    def __init__(self, user, nivel):
        super().__init__(timeout=60)
        self.user = user
        self.nivel = nivel
        self.add_item(ItemDropdown(nivel))

class ItemDropdown(Select):
    def __init__(self, nivel):
        cog = None
        itens_disponiveis = self.get_itens_por_nivel(nivel)

        options = []
        display_names = {
            "madeira": "Tronco de Carvalho",
            "pedra": "Pedregulho",
            "carvao": "Carvão",
            "ferro": "Ferro Bruto",
            "ouro": "Ouro Bruto",
            "diamante": "Diamante",
        }
        for item, preco in itens_disponiveis.items():
            emoji_str = self.get_emoji_for_item(item)
            display_name = display_names.get(item, item.replace('_', ' ').title())
            label = f"{display_name} ({preco} XP)"
            option = discord.SelectOption(
                label=label,
                value=item,
                description=f"Comprar {display_name}"
            )
            if emoji_str:
                option.emoji = emoji_str
            options.append(option)

        if not options:
            options = [discord.SelectOption(label="Nenhum item disponível", value="none", description="Suba de nível para desbloquear itens")]

        super().__init__(
            placeholder="🛍️ Selecione um item...",
            min_values=1,
            max_values=1,
            options=options
        )

    def get_itens_por_nivel(self, nivel):
        """Retorna dicionário de itens disponíveis por nível com preços em XP."""
        itens = {}

        levels_file = "levels.json"
        if os.path.exists(levels_file):
            try:
                with open(levels_file, "r", encoding="utf-8") as f:
                    levels_data = json.load(f)
            except json.JSONDecodeError:
                return itens
        else:
            return itens

        for level_data in levels_data["levels"]:
            if level_data["level"] <= nivel:
                for item in level_data["items"]:
                    if item in ["madeira", "graveto", "semente", "pedra", "carvao", "tocha"]:
                        preco = 1
                    elif item in ["ferro", "cobre", "gelo", "neve", "la", "areia", "cacto", "vidro"]:
                        preco = 5
                    elif item in ["bambu", "cacau", "melancia", "cascalho", "argila", "abobora"]:
                        preco = 10
                    elif item in ["coral", "peixe", "concha_nautilo", "flores_raras", "mudas_especiais"]:
                        preco = 15
                    elif item in ["slime", "muda_cerejeira", "cogumelo", "esmeralda", "livro_encantado", "totem"]:
                        preco = 25
                    elif item in ["quartzo", "glowstone", "magma", "vara_blaze", "fragmento", "ceramica", "item_raro"]:
                        preco = 50
                    elif item in ["eco_shard", "catalisador_sculk", "disco_raro", "olho_ender", "livro_encantado_forte", "obsidiana"]:
                        preco = 100
                    else:
                        preco = 1

                    itens[item] = preco

        return itens

    def get_emoji_for_item(self, item):
        """Retorna o emoji para um item específico."""
        if item in EMOJIS:
            return EMOJIS[item]

        item_lower = item.lower()
        if item_lower in EMOJIS:
            return EMOJIS[item_lower]

        emoji_mappings = {
            "madeira": "tronco de carvalho",
            "graveto": "graveto",
            "semente": "semente",
            "pedra": "pedregulho",
            "carvao": "carvao",
            "tocha": "tocha",
            "ferro": "ferro_bruto",
            "cobre": "cobre",
            "gelo": "gelo",
            "neve": "neve",
            "la": "la",
            "areia": "areia",
            "cacto": "cacto",
            "vidro": "vidro",
            "bambu": "bambu",
            "cacau": "cacau",
            "melancia": "melancia",
            "cascalho": "cascalho",
            "argila": "argila",
            "abobora": "abobora",
            "coral": "coral",
            "peixe": "peixe",
            "concha_nautilo": "concha_nautilo",
            "flores_raras": "flor",
            "mudas_especiais": "muda",
            "slime": "slime",
            "muda_cerejeira": "muda_cerejeira",
            "cogumelo": "cogumelo",
            "esmeralda": "esmeralda",
            "livro_encantado": "livro_encantado",
            "totem": "totem",
            "quartzo": "quartzo",
            "glowstone": "glowstone",
            "magma": "magma",
            "vara_blaze": "vara_blaze",
            "fragmento": "fragmento",
            "ceramica": "ceramica",
            "item_raro": "item_raro",
            "eco_shard": "eco_shard",
            "catalisador_sculk": "catalisador_sculk",
            "disco_raro": "disco_raro",
            "olho_ender": "olho_ender",
            "livro_encantado_forte": "livro_encantado",
            "obsidiana": "obsidiana"
        }

        mapped_item = emoji_mappings.get(item_lower)
        if mapped_item and mapped_item in EMOJIS:
            return EMOJIS[mapped_item]

        return ""

    async def callback(self, interaction: discord.Interaction):
        item = self.values[0]
        if item == "none":
            await interaction.response.send_message(
                f"{EMOJIS['c_negativo']} Nenhum item disponível no seu nível atual!",
                ephemeral=True
            )
            return

        cog = interaction.client.get_cog("Loja")
        if cog:
            await cog.comprar_item(interaction, item, 1)
        else:
            await interaction.response.send_message(
                f"{EMOJIS['c_negativo']} O sistema de loja não está disponível no momento",
                ephemeral=True
            )