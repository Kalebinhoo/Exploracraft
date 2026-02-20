import discord
from discord.ui import Button, View
import random
from icons.emojis_blocos import EMOJIS_BLOCOS
from icons.emojis_minerios import EMOJIS_MINERIOS
from utils.database import adicionar_item, adicionar_moedas
from icons.emojis_icones import EMOJIS_ICONES

class FinalizarButton(Button):
    def __init__(self, game_view, bet, user_id):
        super().__init__(label="Finalizar Jogo", style=discord.ButtonStyle.danger)
        self.game_view = game_view
        self.bet = bet
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if not self.game_view.game_over:
            self.game_view.game_over = True
        revealed_safe = 0
        for y in range(self.game_view.size):
            for x in range(self.game_view.size):
                if not self.game_view.mines[y][x] and self.game_view.board[y][x] != ' ':
                    revealed_safe += 1
        amount = 2 * revealed_safe
        if self.game_view.check_win():
            amount *= 2
        title = f"Você ganhou {amount} Minecoins"
        description = f"Você revelou {revealed_safe} células seguras corretamente."
        if self.game_view.check_win():
            description += " Parabéns! Você venceu o Mines."
            color = 0x00FF00
        else:
            description += " Tente novamente."
            color = 0xFFFF00
        adicionar_moedas(self.user_id, amount)
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        await interaction.response.edit_message(embed=embed, view=None)

class CellButton(Button):
    def __init__(self, x, y, game):
        super().__init__(
            label="⬜",
            style=discord.ButtonStyle.secondary,
            row=y
        )
        self.x = x
        self.y = y
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.game_over:
            return

        if self.game.flag_mode:
            if self.game.board[self.y][self.x] == 'F':
                self.game.board[self.y][self.x] = ' '
                self.label = "⬜"
            else:
                self.game.board[self.y][self.x] = 'F'
                self.label = "🚩"
        else:
            if self.game.mines[self.y][self.x]:
                self.game.game_over = True
                self.emoji = EMOJIS_BLOCOS["tnt"]
                self.label = None
                self.style = discord.ButtonStyle.danger
                await self.game.end_game(interaction, False)
                return
            else:
                count = self.game.count_adjacent_mines(self.x, self.y)
                self.game.board[self.y][self.x] = str(count) if count > 0 else '0'
                self.emoji = EMOJIS_MINERIOS["diamante"]
                self.label = None
                self.disabled = True
                self.style = discord.ButtonStyle.blurple

                if self.game.check_win():
                    self.game.game_over = True
                    await self.game.end_game(interaction, True)
                    return

        await interaction.response.edit_message(view=self.game)
        revealed_safe = sum(1 for y in range(self.game.size) for x in range(self.game.size) if not self.game.mines[y][x] and self.game.board[y][x] != ' ')
        total_safe = self.game.size * self.game.size - self.game.num_mines
        embed = discord.Embed(
            title="💣 Mines - Campo Minado Minecraft",
            description=f"Clique nas células para revelar. Bandeira para marcar minas!\n\nAposta: {self.game.bet} Minecoins\nCélulas reveladas: {revealed_safe}/{total_safe}\n\nUse os botões abaixo para jogar.",
            color=0xFF0000
        )
        await interaction.edit_original_response(embed=embed)

class ModeButton(Button):
    def __init__(self, game):
        super().__init__(
            label="Modo: Revelar",
            style=discord.ButtonStyle.primary
        )
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        self.game.flag_mode = not self.game.flag_mode
        self.label = "Modo: Bandeira" if self.game.flag_mode else "Modo: Revelar"
        await interaction.response.edit_message(view=self.game)

class NewGameButton(Button):
    def __init__(self, game):
        super().__init__(
            label="Novo Jogo",
            style=discord.ButtonStyle.danger
        )
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        self.game.reset()
        embed = discord.Embed(
            title=f"{EMOJIS_BLOCOS['tnt']} Mines - Campo Minado Minecraft",
            description=f"Clique nas células para revelar. Bandeira para marcar minas!\n\nAposta: {self.game.bet} Minecoins\nCélulas reveladas: 0/11\n\nUse os botões abaixo para jogar.",
            color=0xFF0000
        )
        await interaction.response.edit_message(embed=embed, view=self.game)

class MinesView(View):
    def __init__(self, bet=0, user_id=None):
        super().__init__(timeout=300)
        self.bet = bet
        self.user_id = user_id
        self.size = 4
        self.num_mines = 5
        self.reset()
        self.add_item(FinalizarButton(self, bet, user_id))

    def reset(self):
        self.game_over = False
        self.flag_mode = False
        self.mines = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.place_mines()
        self.clear_items()
        self.add_grid_buttons()
        self.add_item(ModeButton(self))
        self.add_item(NewGameButton(self))

    def place_mines(self):
        positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        mine_positions = random.sample(positions, self.num_mines)
        for x, y in mine_positions:
            self.mines[y][x] = True

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.mines[ny][nx]:
                    count += 1
        return count

    def check_win(self):
        for y in range(self.size):
            for x in range(self.size):
                if not self.mines[y][x] and self.board[y][x] == ' ':
                    return False
        return True

    def add_grid_buttons(self):
        for y in range(self.size):
            for x in range(self.size):
                self.add_item(CellButton(x, y, self))

    async def end_game(self, interaction, won):
        if won:
            reward = self.bet * 3
            description = "Parabéns! Você encontrou todas as minas!"
            self.clear_items()
            self.add_item(FinalizarButton(self, reward, str(interaction.user.id)))
        else:
            description = "Você acertou uma mina!"
            self.clear_items()
            self.add_item(FinalizarButton(self, self.bet, str(interaction.user.id)))

        embed = discord.Embed(
            title="🎉 Você venceu!" if won else "💥 Game Over!",
            description=description,
            color=0x00FF00 if won else 0xFF0000
        )
        await interaction.response.edit_message(embed=embed, view=self)