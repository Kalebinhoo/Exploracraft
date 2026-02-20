import discord
import random
from utils.database import possui_item, adicionar_item, adicionar_xp, alterar_vida, get_status, inventarios
from utils.mobs import mobs
from icons.emojis import EMOJIS
from icons.emojis_icones import EMOJIS_ICONES

class BotoesMobs(discord.ui.View):
    def __init__(self, mob, user, mob_health):
        super().__init__(timeout=30)
        self.mob = mob
        self.user = user
        self.mob_health = mob_health
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except:
                pass

    def verificar_espada(self, user_id):
        """Verifica se o jogador tem qualquer tipo de espada"""
        from utils.database import get_inventario
        user_inv_db = get_inventario(str(user_id))
        user_inv_json = inventarios.get(str(user_id), {})
        user_inv = {**user_inv_db, **user_inv_json}
        espadas_permitidas = [
            "Espada de Madeira", "espada de madeira",
            "Espada de Pedra", "espada de pedra",
            "Espada de Ferro", "espada de ferro",
            "Espada de Ouro", "espada de ouro",
            "Espada de Diamante", "espada de diamante"
        ]
        return any(user_inv.get(espada, 0) > 0 for espada in espadas_permitidas)

    @discord.ui.button(label="⚔️ Matar", style=discord.ButtonStyle.danger)
    async def matar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse mob não é seu!", ephemeral=True)

        if not self.verificar_espada(interaction.user.id):
            return await interaction.response.send_message(
                "⚠️ Você não tem uma espada no inventário para matar o mob.",
                ephemeral=True
            )

        dano_jogador = random.randint(4, 8)
        self.mob_health -= dano_jogador

        from utils.mobs import get_dano_mob
        dano_mob = get_dano_mob(interaction.user.id, self.mob)
        vida_apos = alterar_vida(interaction.user.id, -dano_mob)

        if vida_apos <= 3:
            try:
                await interaction.user.send(f"❤️ **Aviso:** Sua vida está baixa! ({vida_apos}/10 corações). Cuide-se!")
            except:
                pass

        if self.mob_health <= 0:
            dados_mob = mobs[self.mob]
            xp_ganho = dados_mob["xp"]
            drop_mensagem = []

            for item_display_name, (min_qtd, max_qtd) in dados_mob["drops"].items():
                qtd = random.randint(min_qtd, max_qtd)
                if qtd > 0:
                    item_name = item_display_name.lower().replace(" ", "")
                    qtd_real = adicionar_item(interaction.user.id, item_name, qtd)
                    drop_mensagem.append(f"{item_display_name}: {qtd_real}x")

            xp_info = adicionar_xp(interaction.user.id, xp_ganho)

            embed = discord.Embed(
                title=f"🎯 Mob Derrotado!",
                description=f"Você matou um **{self.mob}** {dados_mob['emoji']}",
                color=discord.Color.green()
            )

            if drop_mensagem:
                embed.add_field(
                    name="📦 Drops Obtidos",
                    value="\n".join(f"➤ {drop}" for drop in drop_mensagem),
                    inline=False
                )

            xp_texto = f"{EMOJIS['experiencia']} +{xp_info['xp_ganho']} XP"
            if xp_info.get('subiu_nivel', False):
                xp_texto += f"\n🎉 **LEVEL UP!** Nível {xp_info['nivel_atual']}!"
            embed.add_field(
                name=f"{EMOJIS['experiencia']} Experiência",
                value=xp_texto,
                inline=False
            )

            embed.set_thumbnail(url=dados_mob['imagem'])
            embed.set_footer(text="A noite continua...")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            self.stop()
            if self.message:
                try:
                    await self.message.delete()
                except:
                    pass
        else:
            status = get_status(interaction.user.id)
            embed = discord.Embed(
                title=f"⚔️ Combate com {self.mob}",
                description=f"Você atacou o {self.mob} causando {dano_jogador} de dano!\nO {self.mob} contra-atacou causando {dano_mob} de dano!",
                color=discord.Color.orange()
            )
            embed.add_field(name="❤️ Vida do Mob", value=f"{self.mob_health}/{mobs[self.mob]['vida']}", inline=True)
            embed.add_field(name="❤️ Sua Vida", value=f"{status['vida']}/10", inline=True)
            embed.set_image(url=mobs[self.mob]['imagem'])
            embed.set_footer(text="Continue o combate!")

            self.mob_health = self.mob_health
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏃 Fugir", style=discord.ButtonStyle.secondary, emoji=EMOJIS_ICONES['speed'])
    async def fugir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse mob não é seu!", ephemeral=True)

        from utils.database import get_status
        status = get_status(interaction.user.id)
        if status["fome"] <= 0:
            return await interaction.response.send_message(
                "🍽️ Você está com fome demais para correr! Use /comer para se alimentar primeiro.",
                ephemeral=True
            )

        from utils.database import alterar_fome
        alterar_fome(interaction.user.id, -2)

        embed = discord.Embed(
            title="🏃 Fugiu!",
            description=f"Você fugiu do {self.mob}, mas gastou fome.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()
        if self.message:
            try:
                await self.message.delete()
            except:
                pass