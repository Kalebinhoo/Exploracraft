import discord
from discord.ui import Button, View
import random
from icons.emojis_icones import EMOJIS_ICONES
from utils.database import adicionar_moedas, get_moedas

class AcceptButton(Button):
    def __init__(self):
        super().__init__(label="Aceitar Aposta", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if str(interaction.user.id) != view.friend_id:
            await interaction.response.send_message("❌ Apenas o convidado pode aceitar.", ephemeral=True)
            return
        if view.bet > 0:
            balance = get_moedas(view.friend_id)
            if balance < view.bet:
                await interaction.response.send_message("❌ Você não tem Minecoins suficientes.", ephemeral=True)
                return
            adicionar_moedas(view.friend_id, -view.bet)
        view.confirmed = True
        view.clear_items()
        view.add_item(RockButton(view))
        view.add_item(PaperButton(view))
        view.add_item(ScissorsButton(view))
        embed = discord.Embed(
            title="🪨📄✂️ Pedra Papel Tesoura",
            description="Escolha sua jogada:",
            color=0x00AA00
        )
        await interaction.response.edit_message(embed=embed, view=view)

class FinalizarButton(Button):
    def __init__(self, amount, user_id, result_type):
        super().__init__(label="Finalizar Jogo", style=discord.ButtonStyle.danger)
        self.amount = amount
        self.user_id = user_id
        self.result_type = result_type

    async def callback(self, interaction: discord.Interaction):
        adicionar_moedas(self.user_id, self.amount)
        if self.result_type == 'win':
            title = f"Você ganhou {self.amount} Minecoins"
            description = "Parabéns! Você venceu o Pedra Papel Tesoura."
            color = 0x00FF00
        elif self.result_type == 'loss':
            title = f"Você perdeu {self.amount} Minecoins"
            description = "Tente novamente."
            color = 0xFF0000
        else:
            title = f"Empate, devolução {self.amount} Minecoins"
            description = "Sua aposta foi devolvida."
            color = 0xFFFF00
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        await interaction.response.edit_message(embed=embed, view=None)

class RockButton(Button):
    def __init__(self, view):
        super().__init__(
            label="Pedra",
            emoji=EMOJIS_ICONES["pedregulho"],
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.record_choice(interaction, "pedregulho")

class PaperButton(Button):
    def __init__(self, view):
        super().__init__(
            label="Papel",
            emoji=EMOJIS_ICONES["papel"],
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.record_choice(interaction, "papel")

class ScissorsButton(Button):
    def __init__(self, view):
        super().__init__(
            label="Tesoura",
            emoji=EMOJIS_ICONES["tesoura"],
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.record_choice(interaction, "tesoura")

class PlayAgainButton(Button):
    def __init__(self, bet):
        super().__init__(
            label="Jogar Novamente",
            style=discord.ButtonStyle.primary
        )
        self.bet = bet

    async def callback(self, interaction: discord.Interaction):
        view = RockPaperScissorsView(self.bet)
        embed = discord.Embed(
            title="🪨📄✂️ Pedra Papel Tesoura",
            description="Escolha sua jogada:",
            color=0x00AA00
        )
        await interaction.response.edit_message(embed=embed, view=view)

class PlayAgainView(View):
    def __init__(self, bet):
        super().__init__(timeout=None)

        self.add_item(PlayAgainButton(bet))

class RockPaperScissorsView(View):
    def __init__(self, bet=0, friend_id=None, user_id=None):
        super().__init__(timeout=None)
        self.bet = bet
        self.friend_id = friend_id
        self.user_id = user_id
        self.choices = {}
        self.confirmed = not bool(self.friend_id)
        if self.friend_id:
            self.players = [self.user_id, self.friend_id]
        else:
            self.players = [self.user_id]

        if not self.confirmed:
            self.add_item(AcceptButton())
        else:
            self.add_item(RockButton(self))
            self.add_item(PaperButton(self))
            self.add_item(ScissorsButton(self))

    async def record_choice(self, interaction, choice):
        if not self.confirmed:
            await interaction.response.send_message("❌ Aguarde a confirmação da aposta.", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        if user_id not in self.players:
            await interaction.response.send_message("❌ Você não está participando deste jogo.", ephemeral=True)
            return
        if user_id in self.choices:
            await interaction.response.send_message("❌ Você já escolheu.", ephemeral=True)
            return
        self.choices[user_id] = choice
        if len(self.choices) == len(self.players):
            await self.resolve_game(interaction)
        else:
            description = "Aguardando os jogadores escolherem..."
            if self.bet > 0:
                description += f"\n\nAposta: {self.bet} Minecoins"
            embed = discord.Embed(
                title="🪨📄✂️ Pedra Papel Tesoura",
                description=description,
                color=0x00AA00
            )
            await interaction.response.edit_message(embed=embed, view=self)

    async def resolve_game(self, interaction):
        if not self.friend_id:
            user_choice = self.choices[self.user_id]
            bot_choice = random.choice(["pedregulho", "papel", "tesoura"])
            if user_choice == bot_choice:
                if self.bet > 0:
                    result = f"Empate, devolução {self.bet} Minecoins."
                    adicionar_moedas(self.user_id, self.bet)
                else:
                    result = "Empate!"
                color = 0xFFFF00
            elif (user_choice == "pedregulho" and bot_choice == "tesoura") or \
                 (user_choice == "papel" and bot_choice == "pedregulho") or \
                 (user_choice == "tesoura" and bot_choice == "papel"):
                if self.bet > 0:
                    result = f"Você ganhou {self.bet * 2} Minecoins!"
                    reward = self.bet * 2
                    adicionar_moedas(self.user_id, reward)
                else:
                    result = "Você ganhou!"
                color = 0x00FF00
            else:
                if self.bet > 0:
                    result = f"Você perdeu {self.bet} Minecoins."
                else:
                    result = "Você perdeu!"
                color = 0xFF0000
            embed = discord.Embed(
                title="🪨📄✂️ Pedra Papel Tesoura",
                description=f"Você escolheu: {EMOJIS_ICONES[user_choice]}\nBot escolheu: {EMOJIS_ICONES[bot_choice]}\n\n{result}",
                color=color
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            p1_id = self.players[0]
            p2_id = self.players[1]
            p1_choice = self.choices[p1_id]
            p2_choice = self.choices[p2_id]
            p1_name = f"<@{p1_id}>"
            p2_name = f"<@{p2_id}>"
            if p1_choice == p2_choice:
                if self.bet > 0:
                    result = f"Empate! Ambos recuperam {self.bet} Minecoins."
                    adicionar_moedas(p1_id, self.bet)
                    adicionar_moedas(p2_id, self.bet)
                else:
                    result = "Empate!"
                color = 0xFFFF00
            elif (p1_choice == "pedregulho" and p2_choice == "tesoura") or \
                 (p1_choice == "papel" and p2_choice == "pedregulho") or \
                 (p1_choice == "tesoura" and p2_choice == "papel"):
                if self.bet > 0:
                    result = f"{p1_name} ganhou {self.bet * 2} Minecoins!"
                    reward = self.bet * 2
                    adicionar_moedas(p1_id, reward)
                else:
                    result = f"{p1_name} ganhou!"
                color = 0x00FF00
            else:
                if self.bet > 0:
                    result = f"{p2_name} ganhou {self.bet * 2} Minecoins!"
                    reward = self.bet * 2
                    adicionar_moedas(p2_id, reward)
                else:
                    result = f"{p2_name} ganhou!"
                color = 0x00FF00
            embed = discord.Embed(
                title="🪨📄✂️ Pedra Papel Tesoura",
                description=f"{p1_name} escolheu: {EMOJIS_ICONES[p1_choice]}\n{p2_name} escolheu: {EMOJIS_ICONES[p2_choice]}\n\n{result}",
                color=color
            )
            await interaction.response.edit_message(embed=embed, view=None)