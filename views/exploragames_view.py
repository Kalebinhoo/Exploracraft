import discord
from discord.ui import Button, View, Modal, TextInput
from views.mines_view import MinesView
from views.rps_view import RockPaperScissorsView
from icons.emojis_blocos import EMOJIS_BLOCOS
from icons.emojis_icones import EMOJIS_ICONES
from utils.database import get_moedas, adicionar_moedas

class BetModal(Modal):
    def __init__(self, game_type):
        super().__init__(title="Apostar Minecoins")
        self.game_type = game_type

        self.bet_input = TextInput(
            label="Quantidade de Minecoins para apostar",
            placeholder="Digite um número positivo",
            required=True
        )
        self.add_item(self.bet_input)

        if self.game_type == "rps":
            self.friend_input = TextInput(
                label="ID do amigo ou 'ninguem' para jogar sozinho",
                placeholder="Digite o ID do amigo ou 'ninguem'",
                required=True
            )
            self.add_item(self.friend_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bet = int(self.bet_input.value)
            if bet <= 0:
                await interaction.response.send_message("❌ A aposta deve ser um número positivo.", ephemeral=True)
                return

            user_id = str(interaction.user.id)
            balance = get_moedas(user_id)
            if balance < bet:
                await interaction.response.send_message("❌ Você não tem Minecoins suficientes.", ephemeral=True)
                return

            friend_id = None
            if self.game_type == "rps":
                friend_value = self.friend_input.value.strip().lower()
                if friend_value == "ninguem" or not friend_value:
                    friend_id = None
                    bet = 0
                else:
                    try:
                        friend_id = str(int(friend_value))
                    except ValueError:
                        await interaction.response.send_message("❌ ID do amigo inválido. Digite um número ou 'ninguem'.", ephemeral=True)
                        return

            if bet > 0:
                adicionar_moedas(user_id, -bet)
            if friend_id:
                balance_friend = get_moedas(friend_id)
                if balance_friend < bet:
                    await interaction.response.send_message("❌ Seu amigo não tem Minecoins suficientes.", ephemeral=True)
                    return

            if self.game_type == "mines":
                view = MinesView(bet, str(interaction.user.id))
                embed = discord.Embed(
                    title="💣 Mines - Campo Minado Minecraft",
                    description=f"Clique nas células para revelar. Bandeira para marcar minas!\n\nAposta: {bet} Minecoins\nCélulas reveladas: 0/11\n\nUse os botões abaixo para jogar.",
                    color=0xFF0000
                )
                await interaction.response.edit_message(embed=embed, view=view)
            elif self.game_type == "rps":
                view = RockPaperScissorsView(bet, friend_id, str(interaction.user.id))
                if friend_id:
                    description = f"Aguardando <@{friend_id}> aceitar"
                    if bet > 0:
                        description += f" a aposta de {bet} Minecoins."
                    else:
                        description += "."
                    embed = discord.Embed(
                        title="🪨📄✂️ Pedra Papel Tesoura",
                        description=description,
                        color=0x00AA00
                    )
                else:
                    embed = discord.Embed(
                        title="🪨📄✂️ Pedra Papel Tesoura",
                        description="Escolha sua jogada:",
                        color=0x00AA00
                    )
                await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

        except ValueError:
            await interaction.response.send_message("❌ Valor inválido. Digite um número.", ephemeral=True)

class MinesButton(Button):
    def __init__(self):
        super().__init__(
            label="Mines",
            emoji=EMOJIS_BLOCOS["tnt"],
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        modal = BetModal("mines")
        await interaction.response.send_modal(modal)

class RockPaperScissorsButton(Button):
    def __init__(self):
        super().__init__(
            label="",
            emoji=EMOJIS_ICONES["pedregulho"],
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        modal = BetModal("rps")
        await interaction.response.send_modal(modal)

class ExploragamesView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(MinesButton())
        self.add_item(RockPaperScissorsButton())