import discord
from discord.ui import Button, View
from utils.database import clear_travel_state, salvar_inventarios
from utils.models import player_data
from icons.emojis import EMOJIS

class LocationButton(Button):
    def __init__(self, label, emoji, style, action_type):
        super().__init__(label=label, emoji=emoji, style=style)
        self.action_type = action_type

    async def callback(self, interaction: discord.Interaction):
        if self.action_type == "casa":
            embed = discord.Embed(
                title="🏠 Casa",
                description="Você está em casa! Aqui você pode descansar e se preparar para novas aventuras.",
                color=0x8B4513
            )
            embed.set_image(url="https://minecraft.wiki/images/thumb/House.png/800px-House.png")

        elif self.action_type == "villager":
            embed = discord.Embed(
                title="👨‍🌾 Aldeão",
                description="Você encontrou um aldeão! Ele pode ter itens para trocar ou missões para você.",
                color=0x228B22
            )
            embed.set_image(url="https://minecraft.wiki/images/thumb/Villager.png/200px-Villager.png")

        elif self.action_type == "sair":
            clear_travel_state(interaction.user.id)
            player = player_data.get_player(interaction.user.id)
            player["location"] = None
            salvar_inventarios()

            embed = discord.Embed(
                title=f"{EMOJIS['planet']} Expedição Minecraft",
                description="Escolha seu destino:",
                color=0xD3BB94
            )
            embed.set_thumbnail(url="https://minecraft.wiki/images/Compass_JE3_BE3.gif?0043f&format=original")
            embed.set_image(url="https://minecraft.wiki/images/thumb/Map_Zoom_4.png/800px-Map_Zoom_4.png?34c38")

            from views.explorar_view import ExplorarView
            await interaction.response.edit_message(embed=embed, view=ExplorarView())
            return

        await interaction.response.edit_message(embed=embed, view=LocationView())

class LocationView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(LocationButton("Casa", "<:casa:1416047216115843114>", discord.ButtonStyle.secondary, "casa"))
        self.add_item(LocationButton("Aldeão", "<:villagerfazendeiro:1415129946841678014>", discord.ButtonStyle.secondary, "villager"))
        self.add_item(LocationButton("Sair", "<:PortadeCarvalho:1416049338341130381>", discord.ButtonStyle.secondary, "sair"))