import discord
from utils.database import inventarios, salvar_inventarios
from views.view_perfil import BotoesPerfil
from icons.emojis import EMOJIS

class ConfirmarQuebrarMadeiraView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success, emoji=EMOJIS['estrela'])
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)

        user_inv = inventarios.setdefault(str(interaction.user.id), {})
        user_inv["madeira"] = user_inv.get("madeira", 0) + 1
        salvar_inventarios()

        await interaction.response.edit_message(content=f"{EMOJIS['arvorecarvalho']} Você pegou uma madeira!", view=None)

        biome_url = user_inv["bioma_atual"]["url"] if "bioma_atual" in user_inv else ""

        embed = discord.Embed(title=f"{EMOJIS['arvorecarvalho']} Coleta de Madeira", color=discord.Color.green())
        embed.set_image(url=biome_url)
        embed.set_footer(text="Use os botões para coletar mais madeira ou minerar.")
        await interaction.followup.send(embed=embed, view=BotoesPerfil(self.user_id), ephemeral=True)

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
        await interaction.response.edit_message(content=f"{EMOJIS['c_negativo']} Ação cancelada.", view=None)

class BotoesPerfil(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Quebrar Madeira", style=discord.ButtonStyle.primary, emoji=EMOJIS['arvorecarvalho'])
    async def quebrar_madeira(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
        await interaction.response.send_message(
            "Você quer realmente quebrar uma madeira?",
            view=ConfirmarQuebrarMadeiraView(self.user_id),
            ephemeral=True
        )

    @discord.ui.button(label="Minerar", style=discord.ButtonStyle.secondary, emoji=EMOJIS['picareta de ferro'])
    async def minerar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
        await interaction.response.send_message(f"{EMOJIS['picareta de ferro']} Você tentou minerar!", ephemeral=True)
