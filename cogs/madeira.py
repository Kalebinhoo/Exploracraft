import discord
from discord import app_commands
from discord.ext import commands
from views.botoesperfil import ViewMadeira
from utils.database import inventarios, usuarios_coletando, mensagens_coleta
from icons.emojis import EMOJIS

class Madeira(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @app_commands.command(name="madeira", description="Começar a pegar madeira")
    async def madeira(self, interaction: discord.Interaction):
        usuarios_coletando.add(interaction.user.id)

        user_id = str(interaction.user.id)
        biome_url = inventarios[user_id]["bioma_atual"]["url"] if user_id in inventarios and "bioma_atual" in inventarios[user_id] else ""

        embed = discord.Embed(title=f"{EMOJIS['arvorecarvalho']} Coleta de Madeira", color=discord.Color.green())
        embed.set_image(url=biome_url)
        embed.set_footer(text="Clique no botão para coletar madeira.")
        
        view = ViewMadeira(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        if interaction.user.id not in mensagens_coleta:
            mensagens_coleta[interaction.user.id] = []
        
        mensagens_coleta[interaction.user.id].append({
            'channel_id': interaction.channel.id,
            'message_id': (await interaction.original_response()).id
        })

async def setup(client):
    await client.add_cog(Madeira(client))
