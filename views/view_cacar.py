import discord
import random
from utils.database import possui_item, adicionar_item, adicionar_xp, inventarios
from utils.animais import animais
from icons.emojis import EMOJIS
from icons.emojis_icones import EMOJIS_ICONES
from icons.emojis_espadas import EMOJIS_ESPADAS

class BotoesCacar(discord.ui.View):
    def __init__(self, animal, user):
        super().__init__(timeout=30)
        self.animal = animal
        self.user = user

    def verificar_espada(self, user_id):
        """Verifica se o jogador tem qualquer tipo de espada"""
        from utils.database import get_inventario_sqlite
        user_inv_db = get_inventario_sqlite(str(user_id))
        user_inv_json = inventarios.get(str(user_id), {})
        user_inv = {**user_inv_db, **user_inv_json}
        espadas_permitidas = [
            "Espada de Madeira", "espada de madeira",
            "Espada de Pedra", "espada de pedra",
            "Espada de Ferro", "espada de ferro",
            "Espada de Ouro", "espada de ouro",
            "Espada de Diamante", "espada de diamante"
        ]

        def get_quantity(item):
            qty = user_inv.get(item, 0)
            if isinstance(qty, list):
                return sum(qty)
            else:
                return qty

        return any(get_quantity(espada) > 0 for espada in espadas_permitidas)

    @discord.ui.button(label="Matar", emoji=EMOJIS_ESPADAS['espada de ferro'], style=discord.ButtonStyle.danger)
    async def matar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse animal não é seu!", ephemeral=True)

        if not self.verificar_espada(interaction.user.id):
            return await interaction.response.send_message(
                "⚠️ Você não tem uma espada no inventário para matar o animal.", 
                ephemeral=True
            )

        drops = animais[self.animal]["drops"]
        xp_data = animais[self.animal]["xp"]

        if isinstance(xp_data, tuple):
            xp_ganho = random.randint(xp_data[0], xp_data[1])
        else:
            xp_ganho = xp_data

        drop_mensagem = []

        for item_display_name, (min_qtd, max_qtd) in drops.items():
            qtd = random.randint(min_qtd, max_qtd)
            if qtd > 0:
                item_name_mapping = {
                    "Bife": "bifecrua",
                    "Cordeiro": "cordeirocrua",
                    "Frango": "frango",
                    "Costela": "costelacrua",
                    "Lã": "la",
                    "Couro": "couro",
                    "Pena": "pena"
                }

                item_name = item_name_mapping.get(item_display_name, item_display_name.lower())

                qtd_real = adicionar_item(interaction.user.id, item_name, qtd)

                emoji_key = item_name
                display_name = item_name
                if emoji_key and emoji_key in EMOJIS:
                    drop_mensagem.append(f"{EMOJIS[emoji_key]} {display_name}: {qtd_real}x")
                else:
                    drop_mensagem.append(f"{display_name}: {qtd_real}x")

        xp_info = adicionar_xp(interaction.user.id, xp_ganho)
        
        dados_animal = animais[self.animal]
        embed = discord.Embed(
            title=f"🎯 Caça Bem Sucedida!",
            description=f"Você matou um(a) **{self.animal}** {dados_animal['emoji']}",
            color=discord.Color.green()
        )

        drops_texto = []
        for drop in drop_mensagem:
            drops_texto.append(f"➤ {drop}")
        
        if drops_texto:
            embed.add_field(
                name="📦 Drops Obtidos",
                value="\n".join(drops_texto),
                inline=False
            )
        else:
            embed.add_field(
                name="📦 Drops Obtidos",
                value=f"{EMOJIS['c_negativo']} Nenhum item obtido",
                inline=False
            )

        xp_texto = f"{EMOJIS['experiencia']} +{xp_info['xp_ganho']} XP"
        if xp_info.get('subiu_nivel', False):
            xp_texto += f"\n🎉 **LEVEL UP!** Você alcançou o nível {xp_info['nivel_atual']}!"
        embed.add_field(
            name=f"{EMOJIS['experiencia']} Experiência",
            value=xp_texto,
            inline=False
        )

        embed.set_thumbnail(url=dados_animal['imagem'])
        
        embed.add_field(
            name="📋 Informações",
            value=f"Raridade: {dados_animal['raridade'].title()}\nDificuldade: {'⭐' * dados_animal['dificuldade']}",
            inline=True
        )

        embed.set_footer(text="Use /caçar para procurar mais animais!")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

    @discord.ui.button(label="Deixar", emoji=EMOJIS_ICONES['speed'], style=discord.ButtonStyle.secondary)
    async def deixar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse animal não é seu!", ephemeral=True)

        embed = discord.Embed(
            title="🕊️ Animal liberado",
            description="Você deixou o animal fugir.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()