import discord
from utils.database import inventarios, alterar_fome, salvar_inventarios, get_status, get_xp_progresso_atual, calcular_nivel_por_xp
from utils.models import player_data
from icons.emojis import EMOJIS
from icons.emojis_comidas import EMOJIS_COMIDAS
from icons.emojis_icones import EMOJIS_ICONES

def create_bar(current, max_val, length=10):
    """Create a visual bar representation"""
    filled = int((current / max_val) * length)
    empty = length - filled
    return "█" * filled + "░" * empty

class StatusView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)

    async def show_status(self, interaction: discord.Interaction):
        """Show the player's status with bars"""
        status = get_status(int(self.user_id))
        user_data = inventarios.get(self.user_id, {})
        xp_total = user_data.get("xp", 0)
        nivel = calcular_nivel_por_xp(xp_total)
        xp_progress = get_xp_progresso_atual(xp_total, nivel)

        embed = discord.Embed(
            title=f"{EMOJIS_ICONES.get('steve', '👤')} Status do Jogador",
            color=0x270ff
        )

        health_bar = create_bar(status["vida"], 10)
        embed.add_field(
            name=f"{EMOJIS_ICONES.get('vida', '❤️')} Vida",
            value=f"{health_bar} {status['vida']}/10",
            inline=False
        )

        hunger_bar = create_bar(status["fome"], 10)
        embed.add_field(
            name=f"{EMOJIS_ICONES.get('fome', '🍖')} Fome",
            value=f"{hunger_bar} {status['fome']}/10",
            inline=False
        )

        xp_bar = create_bar(xp_progress["progresso"], xp_progress["necessario"])
        embed.add_field(
            name=f"{EMOJIS_ICONES.get('experiencia', '⭐')} Experiência (Nível {nivel})",
            value=f"{xp_bar} {xp_progress['progresso']}/{xp_progress['necessario']}\nFaltam: {xp_progress['faltando']} XP",
            inline=False
        )

        embed.set_footer(text="Use os botões abaixo para gerenciar seu status")

        await interaction.response.send_message(embed=embed, view=self, ephemeral=True)

    @discord.ui.button(label="🍽️ Comer", style=discord.ButtonStyle.primary)
    async def comer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            return await interaction.response.send_message("Este status não é seu!", ephemeral=True)

        user_inv = inventarios.get(self.user_id, {})
        comidas = {
            "maçã": 4, "pão": 5, "carne cozida": 8, "frango cozido": 6, "batata cozida": 5,
            "cenoura dourada": 6, "melancia": 2, "bolo": 2, "biscoito": 2, "sopa de cogumelo": 6,
            "peixe cozido": 5, "maçã dourada": 4, "cenoura": 3, "batata": 1,
            "bifecrua": 0, "bife crua": 0, "frangocrua": 0, "frango cru": 0,
            "cordeirocrua": 0, "cordeiro cru": 0, "costelacrua": 0, "costela crua": 0,
            "salmão cru": 0, "salmão cozido": 5, "bacalhau cru": 0, "bacalhau cozido": 5,
            "torta de abóbora": 8, "torta de maçã": 8, "cogumelo": 2, "cogumelo vermelho": 2, "cogumelo marrom": 2,
            "bifeassado": 8, "frangoassado": 6, "cordeiroassado": 7, "costelaassada": 8
        }

        food_list = []
        food_dict = {}
        index = 1
        for item, qtd in user_inv.items():
            if isinstance(qtd, list):
                total = sum(qtd)
            elif isinstance(qtd, dict):
                total = sum(int(v) for v in qtd.values() if str(v).isdigit()) if qtd else 0
            elif isinstance(qtd, (int, float)):
                total = int(qtd)
            else:
                total = 0
            if total > 0 and item.lower() in [c.lower() for c in comidas.keys()]:
                emoji = EMOJIS_COMIDAS.get(item.lower(), "")
                food_list.append(f"{index}. {emoji} {item} - {total}x")
                food_dict[str(index)] = item
                index += 1

        if not food_list:
            embed = discord.Embed(
                title="🍽️ Inventário Vazio",
                description="Você não tem comidas no inventário!",
                color=0x7270ff
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="🍽️ Escolha uma Comida",
            description="\n".join(food_list),
            color=0x7270ff
        )
        embed.set_footer(text="Clique em 'Selecionar Comida' e digite o número da comida desejada")

        view = FoodSelectionView(self.user_id, food_dict)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class FoodSelectionView(discord.ui.View):
    def __init__(self, user_id, food_dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.food_dict = food_dict

    @discord.ui.button(label="🍽️ Selecionar Comida", style=discord.ButtonStyle.primary)
    async def select_food(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            return await interaction.response.send_message("Este menu não é seu!", ephemeral=True)

        modal = FoodModal(self.user_id, self.food_dict)
        await interaction.response.send_modal(modal)

class FoodModal(discord.ui.Modal, title="Escolher Comida"):
    food_number = discord.ui.TextInput(
        label="Número da Comida",
        placeholder="Digite o número da comida (ex: 1)",
        required=True,
        max_length=2
    )

    def __init__(self, user_id, food_dict):
        super().__init__()
        self.user_id = user_id
        self.food_dict = food_dict

    async def on_submit(self, interaction: discord.Interaction):
        try:
            number = int(self.food_number.value.strip())
            if str(number) not in self.food_dict:
                return await interaction.response.send_message("Número inválido!", ephemeral=True)

            food_item = self.food_dict[str(number)]
            user_inv = inventarios.get(self.user_id, {})

            def get_total_quantity(item_name):
                if item_name not in user_inv:
                    return 0
                qtd = user_inv[item_name]
                if isinstance(qtd, list):
                    return sum(qtd)
                elif isinstance(qtd, dict):
                    return sum(int(v) for v in qtd.values() if str(v).isdigit()) if qtd else 0
                elif isinstance(qtd, (int, float)):
                    return int(qtd)
                else:
                    return 0

            if get_total_quantity(food_item) <= 0:
                return await interaction.response.send_message("Você não tem essa comida!", ephemeral=True)

            from utils.database import get_status
            status = get_status(int(self.user_id))
            if status["fome"] >= 10:
                return await interaction.response.send_message(f"{EMOJIS_ICONES['fome']} Você já está com a fome cheia!", ephemeral=True)

            comidas = {
                "maçã": 4, "pão": 5, "carne cozida": 8, "frango cozido": 6, "batata cozida": 5,
                "cenoura dourada": 6, "melancia": 2, "bolo": 2, "biscoito": 2, "sopa de cogumelo": 6,
                "peixe cozido": 5, "maçã dourada": 4, "cenoura": 3, "batata": 1,
                "bifecrua": 0, "bife crua": 0, "frangocrua": 0, "frango cru": 0,
                "cordeirocrua": 0, "cordeiro cru": 0, "costelacrua": 0, "costela crua": 0,
                "salmão cru": 0, "salmão cozido": 5, "bacalhau cru": 0, "bacalhau cozido": 5,
                "torta de abóbora": 8, "torta de maçã": 8, "cogumelo": 2, "cogumelo vermelho": 2, "cogumelo marrom": 2,
                "bifeassado": 8, "frangoassado": 6, "cordeiroassado": 7, "costelaassada": 8
            }

            if "crua" in food_item.lower() or "cru" in food_item.lower():
                embed = discord.Embed(
                    title="⚠️ Carne Crua!",
                    description=f"**{food_item}** está crua! Você deve cozinhá-la na fornalha antes de comer.",
                    color=discord.Color.orange()
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            recuperacao = comidas.get(food_item.lower(), 0)
            from utils.database import alterar_fome
            alterar_fome(int(self.user_id), recuperacao)

            from utils.database import remover_item
            remover_item(self.user_id, food_item, 1)

            salvar_inventarios()

            embed = discord.Embed(
                title="🍽️ Nham Nham!",
                description=f"Você comeu **{food_item}** e recuperou **{recuperacao}** pontos de fome!",
                color=0x7270ff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError:
            await interaction.response.send_message("Digite um número válido!", ephemeral=True)