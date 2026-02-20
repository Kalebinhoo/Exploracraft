import discord
from discord.ui import Button, View
import random
from datetime import datetime, timedelta
from icons.emojis_biomas import EMOJIS_BIOMAS
from utils.database import set_travel_state, is_user_traveling
import asyncio

class DestinoButton(Button):
    def __init__(self, nome: str, emoji: str, estilo: discord.ButtonStyle):
        super().__init__(
            label=nome,
            emoji=emoji,
            style=estilo
        )
        self.nome = nome
    
    async def callback(self, interaction: discord.Interaction):
        if is_user_traveling(interaction.user.id):
            embed = discord.Embed(
                title="⏳ Você já está viajando!",
                description="Aguarde chegar ao seu destino antes de iniciar uma nova viagem.",
                color=0xFFA500
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.nome == "Vila":
            duracao = 3
        else:
            duracao = random.randint(5, 60)

        chegada = datetime.now() + timedelta(minutes=duracao)

        set_travel_state(interaction.user.id, self.nome, chegada)

        embed = discord.Embed(
            title=f"⏳ Viajando para {self.nome}",
            description=f"Chegada prevista: {chegada.strftime('%H:%M')}\n\nVocê será notificado por DM quando chegar!",
            color=0xF5A623
        )
        embed.set_thumbnail(url=f"https://minecraft.wiki/images/Clock_JE3_BE3.gif?8eaae")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        await self.schedule_arrival_notification(interaction.user, self.nome, duracao)

    async def schedule_arrival_notification(self, user, destination, minutes):
        """Agenda uma notificação de chegada via DM."""
        await asyncio.sleep(minutes * 60)

        try:
            embed = discord.Embed(
                title=f"🎯 Chegada em {destination}!",
                description=f"Você chegou ao seu destino! Use `/explorar` novamente para interagir com o local.",
                color=0x00FF00
            )
            
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

class ExplorarView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        destinos = [
            ("Vila", EMOJIS_BIOMAS["vila"], discord.ButtonStyle.secondary),
        ]

        for nome, emoji, estilo in destinos:
            self.add_item(DestinoButton(nome, emoji, estilo))