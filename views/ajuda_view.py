import discord
from discord.ui import Select, View, Button
from typing import List

class AjudaSelect(Select):
    def __init__(self, categorias: List[dict]):
        options = [
            discord.SelectOption(
                label=cat['nome'],
                description=cat["desc"],
                emoji=cat["emoji"]
            ) for cat in categorias
        ]
        super().__init__(
            placeholder="🌐 Escolha uma categoria...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.categorias = categorias

    async def callback(self, interaction: discord.Interaction):
        categoria_nome = self.values[0]
        categoria = next((cat for cat in self.categorias if cat["nome"] == categoria_nome), None)
        
        if not categoria:
            return await interaction.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
        
        embed = discord.Embed(
            title=f"{categoria['emoji']} **{categoria['nome']}**",
            description=f"*{categoria['detalhes']}*",
            color=0x5865F2
        )
        
        for cmd in categoria["comandos"]:
            embed.add_field(
                name=f"{cmd['emoji']} ```/{cmd['nome']}```",
                value=f"▸ {cmd['desc']}\n{cmd['cooldown']}",
                inline=False
            )
        
        embed.set_footer(text="🔹 Clique em ↪️ para voltar")
        
        await interaction.response.edit_message(
            embed=embed,
            view=CategoriaView(self.categorias, categoria)
        )

class VoltarButton(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji="↪️",
            row=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 **Central de Ajuda - MineBlock**",
            description="✨ Explore todos os comandos disponíveis:\nSelecione uma categoria abaixo para ver os comandos!",
            color=0x5865F2
        )
        embed.set_thumbnail(url="https://i.imgur.com/J5hahC3.png")
        
        view = View()
        view.add_item(AjudaSelect(self.view.categorias))
        
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

class CategoriaView(View):
    def __init__(self, categorias: List[dict], categoria: dict):
        super().__init__(timeout=None)
        self.categorias = categorias
        self.add_item(VoltarButton())

class AjudaView(View):
    def __init__(self, categorias: List[dict]):
        super().__init__(timeout=None)
        self.add_item(AjudaSelect(categorias))