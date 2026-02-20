import discord
from discord import app_commands
from discord.ext import commands
from views.ajuda_view import AjudaView
from icons.emojis import EMOJIS

class AjudaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categorias = [
            {
                "nome": "Sobrevivência",
                "emoji": EMOJIS['arvorecarvalho'],
                "desc": "Comandos básicos de sobrevivência",
                "detalhes": "Comandos essenciais para começar sua aventura!",
                "comandos": [
                    {"nome": "iniciar", "desc": "Comece sua jornada no mundo", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['estrela']},
                    {"nome": "perfil", "desc": "Veja seu perfil", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['livropena']},
                    {"nome": "verperfil", "desc": "Veja perfil de outro jogador", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['livropena']},
                    {"nome": "dormir", "desc": "Descanse para recuperar vida", "cooldown": "⏱️ 5min", "emoji": EMOJIS['cama']},
                    {"nome": "comer", "desc": "Coma para recuperar fome", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['bifecrua']},
                    {"nome": "parar", "desc": "Pare de coletar recursos", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['relogio']}
                ]
            },
            {
                "nome": "Recursos",
                "emoji": EMOJIS['picareta de ferro'],
                "desc": "Coleta e fabricação",
                "detalhes": "Comandos para obter e criar recursos!",
                "comandos": [
                    {"nome": "craft", "desc": "Fabrique itens e ferramentas", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['crafting']},
                    {"nome": "caçar", "desc": "Procure por animais", "cooldown": "⏱️ 15s", "emoji": EMOJIS['cordeirocrua']},
                    {"nome": "madeira", "desc": "Colete madeira", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['arvorecarvalho']},
                    {"nome": "inventario", "desc": "Veja seus itens", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['bau']},
                    {"nome": "drop", "desc": "Doe itens para outros", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['bau']},
                    {"nome": "pararcaçar", "desc": "Pare de caçar", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['relogio']}
                ]
            },
            {
                "nome": "Mundo",
                "emoji": EMOJIS['planet'],
                "desc": "Controle do seu mundo",
                "detalhes": "Comandos para gerenciar seu progresso!",
                "comandos": [
                    {"nome": "loja", "desc": "Compre itens com esmeraldas", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['bau']},
                    {"nome": "saldo", "desc": "Veja seu saldo de Minecoins", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['minecoin']},
                    {"nome": "clear", "desc": "Limpe mensagens", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['bau']},
                    {"nome": "ranking", "desc": "Veja o ranking de mineradores", "cooldown": "⚡ Instantâneo", "emoji": EMOJIS['estrela']},
                    {"nome": "explorar", "desc": "Inicia uma expedição (em manutenção)", "cooldown": "⏱️ Indisponível", "emoji": EMOJIS['planet']}
                ]
            }
        ]

    @app_commands.command(name="ajuda", description="📚  Central de ajuda com todos os comandos")
    async def ajuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{EMOJIS.get('livropena', '📚')} **Central de Ajuda - ExploraCraft**",
            description=f"{EMOJIS['estrela']} Explore todos os comandos disponíveis:\nSelecione uma categoria abaixo para ver os comandos!",
            color=0x5865F2
        )
        embed.set_footer(text=f"🔹 Versão 2.1 | {len(self.categorias)} categorias | {sum(len(cat['comandos']) for cat in self.categorias)} comandos disponíveis")

        try:
            await interaction.user.send(embed=embed, view=AjudaView(self.categorias))
            await interaction.response.send_message(f"{EMOJIS['livropena']} Ajuda enviada no seu DM!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=embed,
                view=AjudaView(self.categorias),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AjudaCog(bot))
