import discord
from discord.ext import commands
from icons.emojis import EMOJIS

class Fornalha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="fornalha", description="Processe itens na sua fornalha (carnes e minérios)!")
    async def fornalha(self, interaction: discord.Interaction):
        from utils.database import inventarios, salvar_inventarios, remover_item, adicionar_item
        user_id = str(interaction.user.id)
        user_inv = inventarios.get(user_id, {})

        def get_total_quantity(value):
            if isinstance(value, list):
                return sum(value)
            else:
                return value

        if get_total_quantity(user_inv.get("Fornalha", 0)) <= 0:
            embed = discord.Embed(
                title="⚠️ Você não tem uma fornalha no inventário",
                description="Para processar itens (carnes e minérios), você precisa craftar uma fornalha usando 8 pedregulhos no /craft.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        itens_processaveis = {
            "costelacrua": "costelaassada",
            "frango": "frangoassado",
            "bifecrua": "bifeassado",
            "cordeirocrua": "cordeiroassado",
            "ferro_bruto": "barradeferro",
            "ouro_bruto": "barradeouro"
        }
        def get_total_quantity(value):
            if isinstance(value, list):
                return sum(value)
            else:
                return value

        itens_encontrados = [(crua, cozida, get_total_quantity(user_inv.get(crua, 0))) for crua, cozida in itens_processaveis.items() if get_total_quantity(user_inv.get(crua, 0)) > 0]

        if not itens_encontrados:
            embed = discord.Embed(
                title=f"{EMOJIS.get('fogo', '🔥')} Nada para processar",
                description="Você não tem itens para processar na fornalha.\nCozinhe carnes cruas ou funda minérios!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        carvao_disponivel = get_total_quantity(user_inv.get("Carvão", 0))
        
        if carvao_disponivel == 0:
            embed = discord.Embed(
                title="⚠️ Sem combustível",
                description="Você precisa de **carvão** para usar a fornalha!\n\n"
                           "💡 **Dica:** Use `/perfil` → **Minerar** para conseguir carvão!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        itens_processados = []
        carvao_usado = 0
        
        for crua, cozida, qtd_disponivel in itens_encontrados:
            if carvao_usado >= carvao_disponivel:
                break
            
            qtd_processar = min(qtd_disponivel, carvao_disponivel - carvao_usado)
            if qtd_processar > 0:
                itens_processados.append((crua, cozida, qtd_processar))
                carvao_usado += qtd_processar

        emoji_mapping = {
            "costelacrua": "costelacrua",
            "frango": "frango",
            "bifecrua": "bifecrua",
            "cordeirocrua": "cordeirocrua",
            "costelaassada": "costelaassada",
            "frangoassado": "frangoassado",
            "bifeassado": "bifeassado",
            "cordeiroassado": "cordeiroassado",
            "ferro_bruto": "ferrobruto",
            "barradeferro": "barradeferro",
            "ouro_bruto": "ourobruto",
            "barradeouro": "barradeouro"
        }

        remover_item(user_id, "Carvão", carvao_usado)
        
        msg = ""
        itens_nao_processados = []
        
        for crua, cozida, qtd in itens_processados:
            remover_item(user_id, crua, qtd)
            adicionar_item(user_id, cozida, qtd)

            emoji_crua = EMOJIS.get(emoji_mapping.get(crua, ""), "")
            emoji_cozida = EMOJIS.get(emoji_mapping.get(cozida, ""), "")

            msg += f"✅ {emoji_crua} {qtd}x {crua} -> {emoji_cozida} {qtd}x {cozida}\n"
        
        for crua, cozida, qtd_original in itens_encontrados:
            qtd_processada = next((qtd for c, co, qtd in itens_processados if c == crua), 0)
            qtd_restante = qtd_original - qtd_processada
            if qtd_restante > 0:
                emoji_crua = EMOJIS.get(emoji_mapping.get(crua, ""), "")
                itens_nao_processados.append(f"{emoji_crua} {qtd_restante}x {crua}")

        carvao_emoji = EMOJIS.get("carvao", "🔥")
        msg += f"\n{carvao_emoji} **Carvão consumido:** {carvao_usado}"
        
        if itens_nao_processados:
            msg += f"\n\n⚠️ **Itens não processados** (falta carvão):\n" + "\n".join(itens_nao_processados)
        
        embed = discord.Embed(
            title=f"{EMOJIS.get('fornalha iluminada', '🔥')} Fornalha - Itens Processados",
            description=msg,
            color=discord.Color.green()
        )
        user_inv = inventarios.get(user_id, {})
        embed.set_footer(text=f"Carvão restante: {get_total_quantity(user_inv.get('Carvão', 0))}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fornalha(bot))
