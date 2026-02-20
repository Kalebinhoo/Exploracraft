import discord
from discord import app_commands
from discord.ext import commands
import random

from utils.biomas import get_madeira_do_bioma, get_nome_bioma
from utils.database import inventarios, salvar_inventarios, usuarios_coletando, vezes_explorar, adicionar_item
from views.botoesperfil import BotoesIniciar
from icons.emojis import EMOJIS

class DificuldadeView(discord.ui.View):
    def __init__(self, user_id, bot):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.bot = bot
        self.dificuldade_escolhida = None

    @discord.ui.button(label="Fácil", style=discord.ButtonStyle.success, emoji=EMOJIS.get('carvao', '⚫'))
    async def facil(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Este menu não é para você!", ephemeral=True)

        self.dificuldade_escolhida = "facil"
        user_id_str = str(self.user_id)
        inventarios.setdefault(user_id_str, {})["dificuldade"] = "facil"
        salvar_inventarios()

        embed = discord.Embed(
            title="✅ Dificuldade Selecionada!",
            description="Você escolheu a dificuldade **Fácil**!\n\nMobs causam menos dano e drops são mais frequentes.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

        await self.continuar_inicio(interaction)

    @discord.ui.button(label="Normal", style=discord.ButtonStyle.primary, emoji=EMOJIS.get('barradeferro', '🔩'))
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Este menu não é para você!", ephemeral=True)

        self.dificuldade_escolhida = "normal"
        user_id_str = str(self.user_id)
        inventarios.setdefault(user_id_str, {})["dificuldade"] = "normal"
        salvar_inventarios()

        embed = discord.Embed(
            title="✅ Dificuldade Selecionada!",
            description="Você escolheu a dificuldade **Normal**!\n\nEquilibrado entre desafio e recompensas.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

        await self.continuar_inicio(interaction)

    @discord.ui.button(label="Difícil", style=discord.ButtonStyle.danger, emoji=EMOJIS.get('barradeouro', '🪙'))
    async def dificil(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Este menu não é para você!", ephemeral=True)

        self.dificuldade_escolhida = "dificil"
        user_id_str = str(self.user_id)
        inventarios.setdefault(user_id_str, {})["dificuldade"] = "dificil"
        salvar_inventarios()

        embed = discord.Embed(
            title="✅ Dificuldade Selecionada!",
            description="Você escolheu a dificuldade **Difícil**!\n\nMobs causam mais dano, mas as recompensas são maiores!",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

        await self.continuar_inicio(interaction)

    async def continuar_inicio(self, interaction: discord.Interaction):
        """Continua o processo de início após selecionar a dificuldade"""
        user_id = str(interaction.user.id)

        biomas = [
            "https://minecraft.wiki/images/thumb/Cherry_Grove.png/600px-Cherry_Grove.png?fd915",
            "https://pt.minecraft.wiki/images/thumb/Forest.png/600px-Forest.png?cddc0",
            "https://minecraft.wiki/images/thumb/Birch_Forest.png/600px-Birch_Forest.png?c72b9",
            "https://minecraft.wiki/images/thumb/Dark_Forest.png/600px-Dark_Forest.png?f84df",
            "https://minecraft.wiki/images/thumb/Giant_Tree_Taiga.png/600px-Giant_Tree_Taiga.png?adba8",
            "https://minecraft.wiki/images/thumb/Jungle.png/600px-Jungle.png?f8caa",
            "https://minecraft.wiki/images/thumb/Savanna.png/600px-Savanna.png?c0845",
            "https://minecraft.wiki/images/Mangrove_Swamp.png?49200"
        ]

        inventarios.setdefault(user_id, {})["registrado"] = True

        registered_count = sum(1 for user_data in inventarios.values() if isinstance(user_data, dict) and user_data.get("registrado"))

        try:
            owner = self.bot.get_user(1435373313776947273)
            if owner:
                embed_dm = discord.Embed(
                    title=f"{EMOJIS.get('amigos', '👥')} Novo Amigo Registrado!",
                    description=f"Um novo jogador se registrou no ExploraCraft!",
                    color=discord.Color.from_rgb(54, 4, 135)
                )
                embed_dm.add_field(
                    name=f"{EMOJIS.get('steve', '👨')} Jogador",
                    value=f"{interaction.user.mention}\n{interaction.user.name}#{interaction.user.discriminator}",
                    inline=True
                )
                embed_dm.add_field(
                    name=f"{EMOJIS.get('online', '🟢')} Número de Registro",
                    value=f"#{registered_count}",
                    inline=True
                )
                embed_dm.add_field(
                    name=f"{EMOJIS.get('casa', '🏠')} Servidor",
                    value=interaction.guild.name if interaction.guild else "DM",
                    inline=True
                )
                embed_dm.set_thumbnail(url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else (interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url))
                embed_dm.set_footer(text=f"ID: {interaction.user.id}")

                await owner.send(embed=embed_dm)
        except Exception as e:
            print(f"Erro ao enviar DM para o dono: {e}")

        usuarios_coletando.add(interaction.user.id)
        vezes_explorar.setdefault(interaction.user.id, 0)

        bioma_escolhido = random.choice(biomas)
        bioma_data = {
            "url": bioma_escolhido,
            "nome": get_nome_bioma(bioma_escolhido),
            "madeira": get_madeira_do_bioma(bioma_escolhido)
        }
        inventarios[user_id]["bioma_atual"] = bioma_data
        tipo_madeira = bioma_data["madeira"]
        adicionar_item(user_id, tipo_madeira, 1)
        salvar_inventarios()

        nome_bioma = get_nome_bioma(bioma_escolhido)
        embed_madeira = discord.Embed(
            title=f"{EMOJIS['relogio']} Mundo iniciado!",
            description=f"Você está em um(a) {nome_bioma}!",
            color=0x9C59B6
        )
        embed_madeira.set_image(url=bioma_escolhido)
        embed_madeira.set_footer(text="Clique no botão para coletar madeira!")
        await interaction.followup.send(
            embed=embed_madeira,
            view=BotoesIniciar(interaction.user.id),
            ephemeral=True
        )

class Iniciar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="iniciar", description="Inicie sua aventura em ExploraCraft!")
    async def iniciar(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        usuario = interaction.user.mention

        biomas = [
            "https://minecraft.wiki/images/thumb/Cherry_Grove.png/600px-Cherry_Grove.png?fd915",
            "https://pt.minecraft.wiki/images/thumb/Forest.png/600px-Forest.png?cddc0",
            "https://minecraft.wiki/images/thumb/Birch_Forest.png/600px-Birch_Forest.png?c72b9",
            "https://minecraft.wiki/images/thumb/Dark_Forest.png/600px-Dark_Forest.png?f84df",
            "https://minecraft.wiki/images/thumb/Giant_Tree_Taiga.png/600px-Giant_Tree_Taiga.png?adba8",
            "https://minecraft.wiki/images/thumb/Jungle.png/600px-Jungle.png?f8caa",
            "https://minecraft.wiki/images/thumb/Savanna.png/600px-Savanna.png?c0845",
            "https://minecraft.wiki/images/Mangrove_Swamp.png?49200"
        ]

        if user_id in inventarios and "registrado" in inventarios[user_id]:
            embed = discord.Embed(
                title=f"{EMOJIS['c_negativo']} Já Registrado",
                description="Você já está registrado no jogo! Não precisa usar /iniciar novamente.\n\nUse outros comandos como:\n- `/madeira` para coletar madeira\n- `/cacar` para caçar animais\n- `/perfil` para ver seu perfil\n- `/ajuda` para ver a lista de comandos",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed_boas_vindas = discord.Embed(
            title=f"{EMOJIS['livropena']} Bem-vindo ao ExploraCraft!",
            color=discord.Color.purple()
        )
        embed_boas_vindas.add_field(
            name=f"{EMOJIS['planet']} Aventura",
            value=(
                f"{usuario}, prepare-se para se aventurar!\n"
                f"{EMOJIS['bau']} Interaja com objetos e sobreviva em um mundo de blocos.\n"
                f"{EMOJIS['espada de ferro']} Encontre recursos, enfrente zumbis e sobreviva!"
            ),
            inline=False
        )
        embed_boas_vindas.set_thumbnail(url="https://i.pinimg.com/originals/e5/3b/74/e53b7448d653e93d37bbaeda27779868.gif")
        embed_boas_vindas.set_image(url="https://i.pinimg.com/736x/f4/64/58/f464588a7e1899b84ed0a4ad27d2e6c7.jpg")
        embed_boas_vindas.set_footer(text="ExploraCraft - Sua aventura começa agora!")

        await interaction.response.send_message(embed=embed_boas_vindas)

        embed_dificuldade = discord.Embed(
            title="🎮 Escolha sua Dificuldade",
            description="Selecione o nível de dificuldade para sua aventura no ExploraCraft!\n\n"
                       f"{EMOJIS['carvao']} **Fácil**: Mobs causam menos dano, drops são mais frequentes\n"
                       f"{EMOJIS['barradeferro']} **Normal**: Equilibrado entre desafio e recompensas\n"
                       f"{EMOJIS['barradeouro']} **Difícil**: Mobs causam mais dano, mas recompensas são maiores!",
            color=0x9C59B6
        )
        embed_dificuldade.set_thumbnail(url="https://i.pinimg.com/originals/e5/3b/74/e53b7448d653e93d37bbaeda27779868.gif")
        embed_dificuldade.set_footer(text="Sua escolha afetará o dano dos mobs e as recompensas!")

        view = DificuldadeView(interaction.user.id, self.bot)
        await interaction.followup.send(embed=embed_dificuldade, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Iniciar(bot))

