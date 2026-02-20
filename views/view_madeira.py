import discord
from discord.ui import View, Button
import json
import random
from utils.biomas import get_madeira_do_bioma, get_emoji_madeira
from utils.database import inventarios, salvar_inventarios
from icons.emojis import EMOJIS

class ViewMadeira(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BotaoMadeira())

class BotaoMadeira(Button):
    def __init__(self):
        super().__init__(
            label="Coletar Madeira",
            style=discord.ButtonStyle.green,
            emoji=EMOJIS['machado de madeira'],
            custom_id="madeira_button"
        )

    async def callback(self, interaction: discord.Interaction):
        view = ConfirmarMadeira()
        embed = discord.Embed(
            title="Confirmar Coleta",
            description="Você tem certeza que deseja coletar madeira?",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmarMadeira(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BotaoConfirmarMadeira())
        self.add_item(BotaoCancelarMadeira())

class BotaoConfirmarMadeira(Button):
    def __init__(self):
        super().__init__(
            label="Sim",
            style=discord.ButtonStyle.green,
            emoji=EMOJIS['estrela'],
            custom_id="confirmar_madeira"
        )

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id not in inventarios:
            inventarios[user_id] = {}

        info_bioma = inventarios[user_id].get("bioma_atual")
        if not info_bioma:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Erro: Bioma não encontrado!", ephemeral=True)
            return

        madeira_bioma = get_madeira_do_bioma(info_bioma["url"])
        emoji_madeira = get_emoji_madeira(info_bioma["url"])

        items = {
            madeira_bioma: {"chance": 1.0, "quantidade": random.randint(1, 3)}
        }

        collected_items = []
        for item, data in items.items():
            if random.random() < data["chance"]:
                quantidade = data["quantidade"]
                if item not in inventarios[user_id]:
                    inventarios[user_id][item] = quantidade
                else:
                    inventarios[user_id][item] += quantidade
                collected_items.append(f"{item} x{quantidade}")

        salvar_inventarios()

        emoji = get_emoji_madeira(info_bioma["url"])

        if collected_items:
            embed = discord.Embed(
                title=f"{emoji} Coleta bem sucedida!",
                description=f"Você coletou:\n" + "\n".join(f"{emoji} {item}" for item in collected_items),
                color=discord.Color.green()
            )
            embed.set_image(url=info_bioma["url"])
        else:
            embed = discord.Embed(
                title="😕 Coleta sem sucesso",
                description="Você não encontrou nada desta vez...",
                color=discord.Color.red()
            )
            embed.set_image(url=info_bioma["url"])

        view = ViewMadeira()
        await interaction.response.send_message(embed=embed, view=view)

class BotaoCancelarMadeira(Button):
    def __init__(self):
        super().__init__(
            label="Não",
            style=discord.ButtonStyle.red,
            emoji=EMOJIS['c_negativo'],
            custom_id="cancelar_madeira"
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Coleta Cancelada",
            description="Você cancelou a coleta de madeira.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
