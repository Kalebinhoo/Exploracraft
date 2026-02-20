import discord
from utils.saves import carregar_mundo
from icons.emojis import EMOJIS

class CarregarMundoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = str(user_id)

    @discord.ui.button(label="🌍 Mundo 1", style=discord.ButtonStyle.green)
    async def mundo_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.carregar(interaction, "mundo_1", "🌍 Mundo 1")

    @discord.ui.button(label="🌍 Mundo 2", style=discord.ButtonStyle.green)
    async def mundo_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.carregar(interaction, "mundo_2", "🌍 Mundo 2")

    @discord.ui.button(label="🌍 Mundo 3", style=discord.ButtonStyle.green)
    async def mundo_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.carregar(interaction, "mundo_3", "🌍 Mundo 3")

    async def carregar(self, interaction: discord.Interaction, slot, nome_mundo):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse menu não é seu!", ephemeral=True)

        bioma_url = carregar_mundo(self.user_id, slot)
        if bioma_url is None:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Nenhum bioma salvo nesse slot!", ephemeral=True)

        embed = discord.Embed(
            title=f"🌄 {nome_mundo} carregado com sucesso!",
            description="Você retornou ao seu mundo salvo.",
            color=discord.Color.green()
        )
        embed.set_image(url=bioma_url)

        await interaction.response.edit_message(embed=embed, view=None)
