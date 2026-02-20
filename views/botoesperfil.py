import discord
import random
import time
from datetime import datetime
from utils.database import inventarios, salvar_inventarios, usuarios_coletando, mensagens_coleta, possui_item, adicionar_item, adicionar_blocos_quebrados
from utils.biomas import get_madeira_do_bioma, get_emoji_madeira
from icons.emojis import EMOJIS
from icons.emojis_minerios import EMOJIS_MINERIOS

class BotoesIniciar(discord.ui.View):
    """View apenas com o botão de madeira para o comando /iniciar"""
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Madeira", emoji="<:arvorecarvalho:1410988171063201863>", style=discord.ButtonStyle.secondary)
    async def madeira(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return
        await interaction.response.send_message(
            content="Você tem certeza que quer quebrar essa madeira?",
            view=ConfirmarQuebrarMadeiraView(self.user_id),
            ephemeral=True
        )

class BotoesPerfil(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Madeira", emoji="<:arvorecarvalho:1410988171063201863>", style=discord.ButtonStyle.secondary)
    async def madeira(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return
        await interaction.response.send_message(
            content="Você tem certeza que quer pegar essa madeira?",
            view=ConfirmarQuebrarMadeiraView(self.user_id),
            ephemeral=True
        )

    @discord.ui.button(label="Minerar", emoji="<:picaretaferro:1401450479401304094>", style=discord.ButtonStyle.secondary)
    async def minerar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        user_inv = inventarios.setdefault(user_id, {})

        picaretas_disponiveis = []
        for nome, qtd in user_inv.items():
            if "picareta" in nome.lower() and (isinstance(qtd, list) and sum(qtd) > 0 or isinstance(qtd, (int, float)) and qtd > 0):
                picaretas_disponiveis.append(nome.lower())

        if not picaretas_disponiveis:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você precisa de uma **Picareta** para minerar!", ephemeral=True)
            return

        nivel_picareta = 0
        if any("diamante" in p or "diamond" in p for p in picaretas_disponiveis):
            nivel_picareta = 5
        elif any("ouro" in p or "gold" in p for p in picaretas_disponiveis):
            nivel_picareta = 4
        elif any("ferro" in p or "iron" in p for p in picaretas_disponiveis):
            nivel_picareta = 3
        elif any("pedra" in p or "stone" in p for p in picaretas_disponiveis):
            nivel_picareta = 2
        elif any("madeira" in p or "wood" in p for p in picaretas_disponiveis):
            nivel_picareta = 1

        qtd_ouro_bruto = 0
        qtd_diamante_bruto = 0

        if nivel_picareta >= 4:
            qtd_pedregulho = random.randint(2, 20)

            qtd_carvao = 0
            if random.random() < 0.5:
                qtd_carvao = random.randint(1, 37)

            qtd_ferro_bruto = 0
            if random.random() < 0.4:
                qtd_ferro_bruto = random.randint(1, 13)

            if random.random() < 0.3:
                qtd_ouro_bruto = random.randint(1, 10)

            qtd_diamante_bruto = 0
            if random.random() < 0.06:
                qtd_diamante_bruto = random.randint(1, 8)
        elif nivel_picareta == 3:
            qtd_pedregulho = random.randint(1, 18)
            qtd_carvao = random.randint(1, 20)

            qtd_ferro_bruto = 0
            if random.random() < 0.4:
                qtd_ferro_bruto = random.randint(1, 13)
        elif nivel_picareta == 2:
            qtd_pedregulho = random.randint(1, 16)
            qtd_carvao = random.randint(1, 18)

            qtd_ferro_bruto = 0
            if random.random() < 0.3:
                qtd_ferro_bruto = random.randint(1, 10)

        if nivel_picareta >= 2:
            qtd_real_pedregulho = adicionar_item(user_id, "Pedregulho", qtd_pedregulho)

            qtd_real_carvao = adicionar_item(user_id, "Carvão", qtd_carvao)

            qtd_real_ferro = adicionar_item(user_id, "ferro_bruto", qtd_ferro_bruto) if qtd_ferro_bruto > 0 else 0

            qtd_real_ouro = 0
            if nivel_picareta >= 4 and 'qtd_ouro_bruto' in locals() and qtd_ouro_bruto > 0:
                qtd_real_ouro = adicionar_item(user_id, "ouro_bruto", qtd_ouro_bruto)

            qtd_real_diamante = 0
            if 'qtd_diamante_bruto' in locals() and qtd_diamante_bruto > 0:
                qtd_real_diamante = adicionar_item(user_id, "diamante", qtd_diamante_bruto)

            mensagem_limite = ""
            limite_items = []
            if qtd_real_pedregulho < qtd_pedregulho:
                limite_items.append("Pedregulho")
            if qtd_real_carvao < qtd_carvao:
                limite_items.append("Carvão")
            if qtd_ferro_bruto > 0 and qtd_real_ferro < qtd_ferro_bruto:
                limite_items.append("Ferro Bruto")
            if qtd_ouro_bruto > 0 and qtd_real_ouro < qtd_ouro_bruto:
                limite_items.append("Ouro Bruto")
            if qtd_diamante_bruto > 0 and qtd_real_diamante < qtd_diamante_bruto:
                limite_items.append("Diamante")

            if limite_items:
                mensagem_limite = f"\n⚠️ {', '.join(limite_items)} atingiram o limite de 64 no inventário!"

            desc_parts = [
                f"<:pedregulho:1391151677930868880> Pedregulho: {qtd_real_pedregulho}"
            ]
            if qtd_real_carvao > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['Carvão']} Carvão: {qtd_real_carvao}")
            if qtd_real_ferro > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['ferro_bruto']} Ferro Bruto: {qtd_real_ferro}")
            if qtd_real_ouro > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['ouro_bruto']} Ouro Bruto: {qtd_real_ouro}")
            if qtd_real_diamante > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['diamante']} Diamante: {qtd_real_diamante}")

            embed = discord.Embed(
                title="<:picaretaferro:1401450479401304094> Mineração realizada!",
                description=f"Você minerou e encontrou:\n" + "\n".join(desc_parts) + mensagem_limite,
                color=discord.Color.dark_gray()
            )
        else:
            qtd_pedregulho = random.randint(1, 18)
            qtd_carvao = random.randint(1, 15)

            qtd_real_pedregulho = adicionar_item(user_id, "Pedregulho", qtd_pedregulho)

            qtd_real_carvao = adicionar_item(user_id, "Carvão", qtd_carvao)

            mensagem_limite = ""
            if qtd_real_pedregulho < qtd_pedregulho or qtd_real_carvao < qtd_carvao:
                mensagem_limite = "\n⚠️ Alguns itens atingiram o limite de 64 no inventário!"

            embed = discord.Embed(
                title="<:picaretaferro:1401450479401304094> Mineração realizada!",
                description=f"Você minerou e encontrou:\n<:pedregulho:1391151677930868880> Pedregulho: {qtd_real_pedregulho}\n{EMOJIS_MINERIOS['Carvão']} Carvão: {qtd_real_carvao}{mensagem_limite}",
                color=discord.Color.dark_gray()
            )
        embed.set_image(url="https://minecraft.wiki/images/8/8c/Cave.png")
        embed.set_footer(text="Use sua picareta para encontrar recursos valiosos!")

        def get_total_quantity(value):
            if isinstance(value, list):
                return sum(value)
            else:
                return value

        has_pickaxe_left = any(get_total_quantity(qtd) > 0 for nome, qtd in user_inv.items() if "picareta" in nome.lower())

        if has_pickaxe_left:
            await interaction.response.send_message(
                embed=embed,
                view=MineracaoResultViewPerfil(self.user_id),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

    @discord.ui.button(label="Plantar", emoji="<:trigo:1410991160272617493>", style=discord.ButtonStyle.secondary)
    async def plantar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        embed = discord.Embed(
            title="<:trigo:1410991160272617493> Sistema de Plantação",
            color=discord.Color.green()
        )

        plantacao = user_inv.get("plantacao_ativa", None)

        if plantacao:
            tempo_atual = datetime.now().timestamp()
            tempo_restante = plantacao["tempo_colheita"] - tempo_atual

            tipo = plantacao["tipo"]

            if tempo_restante <= 0:
                embed.description = f"<:crescimentofinal:1414257101877805196> **{tipo.title()} PRONTO PARA COLHER!**"
                embed.color = discord.Color.gold()
                imagens_maduras = {
                    "trigo": "https://minecraft.wiki/images/2/29/Wheat_Age_7.png"
                }
                embed.set_image(url=imagens_maduras.get(tipo, imagens_maduras["trigo"]))
                embed.add_field(name="⏰ Status", value="**COLHEITA DISPONÍVEL** ✅", inline=True)
            else:
                horas = int(tempo_restante // 3600)
                minutos = int((tempo_restante % 3600) // 60)
                segundos = int(tempo_restante % 60)

                if horas > 0:
                    tempo_texto = f"{horas}h {minutos}m"
                else:
                    tempo_texto = f"{minutos}m {segundos}s"

                embed.description = f"<:crescimentomedio:1414261209267437638> **{tipo.title()}** crescendo..."
                embed.color = discord.Color.orange()
                imagens_crescendo = {
                    "trigo": "https://minecraft.wiki/images/9/94/Wheat_Age_3.png"
                }
                embed.set_image(url=imagens_crescendo.get(tipo, imagens_crescendo["trigo"]))
                embed.add_field(name="⏰ Tempo Restante", value=f"**{tempo_texto}**", inline=True)

                tempo_colheita = datetime.fromtimestamp(plantacao["tempo_colheita"])
                embed.add_field(
                    name="🕐 Pronto em",
                    value=tempo_colheita.strftime("%d/%m/%Y às %H:%M"),
                    inline=True
                )
        else:
            embed.description = "<:crescimentofinal:1414257101877805196> **Nenhuma plantação ativa**\nClique em **Plantar** para começar!"
            embed.set_image(url="https://minecraft.wiki/images/c/c1/Farmland.png")
            embed.add_field(name="<a:relogio:1414262811626045541> Tempo de Crescimento", value="**24 horas** ⏰", inline=True)

        embed.set_footer(text="<:trigo:1410991160272617493> Gerencie suas plantações aqui!")

        await interaction.response.send_message(
            embed=embed,
            view=PlantacaoView(self.user_id),
            ephemeral=True
        )

class ViewMadeira(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Madeira", emoji="<:arvorecarvalho:1410988171063201863>", style=discord.ButtonStyle.secondary)
    async def madeira(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return
        await interaction.response.send_message(
            content="Você tem certeza que quer pegar essa madeira?",
            view=ConfirmarQuebrarMadeiraView(self.user_id),
            ephemeral=True
        )

class ConfirmarQuebrarMadeiraView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="✅ Sim", style=discord.ButtonStyle.secondary)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        user_inv = inventarios.setdefault(user_id, {})

        if interaction.user.id not in usuarios_coletando:
            usuarios_coletando.add(interaction.user.id)

        bioma_atual = user_inv.get("bioma_atual", {})
        bioma_url = bioma_atual.get("url", "")

        tipo_madeira = get_madeira_do_bioma(bioma_url)
        emoji_madeira = get_emoji_madeira(bioma_url)

        def get_total(qtd):
            if isinstance(qtd, list):
                return sum(qtd)
            else:
                return qtd

        tem_machado = any(get_total(qtd) > 0 for nome, qtd in user_inv.items() if "machado" in nome.lower())

        if tem_machado:
            madeira_coletada = 2
            adicionar_item(user_id, tipo_madeira, madeira_coletada)
            mensagem = f"🪓 Você usou seu machado de madeira e coletou {madeira_coletada} {emoji_madeira} {tipo_madeira}!"
        else:
            madeira_coletada = 1
            adicionar_item(user_id, tipo_madeira, madeira_coletada)
            mensagem = f"Você coletou {madeira_coletada} {emoji_madeira} {tipo_madeira} com suas mãos!"

        await interaction.response.edit_message(content=mensagem, view=None)

        import asyncio
        await asyncio.sleep(2)

        if interaction.user.id in usuarios_coletando:
            embed_nova = discord.Embed(title=f"<:arvorecarvalho:1410988171063201863> Coleta de Madeira - {bioma_atual.get('nome', 'Desconhecido')}", color=discord.Color.green())
            embed_nova.set_image(url=bioma_url)
            embed_nova.set_footer(text="Clique no botão para coletar mais madeira.")
            followup_msg = await interaction.followup.send(embed=embed_nova, view=BotoesIniciar(self.user_id), ephemeral=True)

            if interaction.user.id not in mensagens_coleta:
                mensagens_coleta[interaction.user.id] = []

            mensagens_coleta[interaction.user.id].append({
                'channel_id': interaction.channel.id,
                'message_id': followup_msg.id
            })

            async def delete_collection_message():
                await asyncio.sleep(5)
                try:
                    await interaction.delete_original_response()
                except:
                    pass

            asyncio.create_task(delete_collection_message())

    @discord.ui.button(label="❌ Não", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
            return

        await interaction.response.edit_message(content=f"{EMOJIS['c_negativo']} Coleta de madeira cancelada.", view=None)

class EscolherSementeView(discord.ui.View):
    def __init__(self, user_id, sementes_disponiveis):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.sementes_disponiveis = sementes_disponiveis

        if "trigo" in sementes_disponiveis:
            self.add_item(PlantarButton("🌾", "trigo", "Trigo"))

class PlantarButton(discord.ui.Button):
    def __init__(self, emoji, tipo_semente, nome_semente):
        super().__init__(emoji=emoji, label=f"Plantar {nome_semente}", style=discord.ButtonStyle.success)
        self.tipo_semente = tipo_semente
        self.nome_semente = nome_semente

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user.id != view.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        semente_key = f"sementes_{self.tipo_semente}"
        if user_inv.get(semente_key, 0) <= 0:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem sementes de {self.nome_semente}!", ephemeral=True)
            return

        if user_inv.get("plantacao_ativa"):
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você já tem uma plantação ativa! Colha ela primeiro.", ephemeral=True)
            return

        user_inv[semente_key] -= 1

        tempo_atual = datetime.now().timestamp()
        tempo_colheita = tempo_atual + 86400

        user_inv["plantacao_ativa"] = {
            "tipo": self.tipo_semente,
            "tempo_plantio": tempo_atual,
            "tempo_colheita": tempo_colheita
        }

        salvar_inventarios()

        tempo_restante = 86400
        horas = tempo_restante // 3600

        imagens = {
            "trigo": "https://minecraft.wiki/images/2/26/Wheat_Age_0.png"
        }

        embed = discord.Embed(
            title="<:crescimentoinicial:1414259929191284756> Plantação Realizada!",
            description=f"Você plantou **{self.nome_semente}**!\n\n"
                        f"⏰ **Tempo para crescer: 24 horas**\n"
                        f"<:trigo:1410991160272617493> A plantação crescerá automaticamente, mesmo quando você estiver offline!\n"
                        f"<a:relogio:1414262811626045541> Use `/perfil` e clique em **Colher** amanhã!",
            color=discord.Color.green()
        )

        embed.add_field(
            name="⏰ Tempo Restante",
            value=f"🕐 {int(horas)} horas",
            inline=True
        )

        embed.set_image(url=imagens.get(self.tipo_semente, imagens["trigo"]))
        embed.set_footer(text=f"Plantado: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")

        await interaction.response.edit_message(embed=embed, view=None)

class StatusPlantacaoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="📊 Ver Status", style=discord.ButtonStyle.primary)
    async def ver_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        plantacoes = user_inv.get("plantacoes", {})

        if not plantacoes:
            await interaction.response.send_message("🌱 Você não tem plantações ativas!", ephemeral=True)
            return

        tempo_atual = time.time()

        embed = discord.Embed(
            title="🌾 Status das Plantações",
            color=discord.Color.green()
        )

        for tipo, dados in plantacoes.items():
            tempo_restante = dados["tempo_colheita"] - tempo_atual

            if tempo_restante <= 0:
                status = "✅ **PRONTO PARA COLHER!**"
            else:
                minutos = int(tempo_restante // 60)
                segundos = int(tempo_restante % 60)
                status = f"⏰ {minutos}m {segundos}s restantes"

            emoji = {"trigo": "🌾"}.get(tipo, "🌱")
            embed.add_field(
                name=f"{emoji} {tipo.title()}",
                value=status,
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class MineracaoResultViewPerfil(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="Minerar Novamente", style=discord.ButtonStyle.secondary, emoji="<:picaretaferro:1401450479401304094>")
    async def minerar_novamente(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        await interaction.response.defer()

        loading_embed = discord.Embed(
            title="<:picaretaferro:1401450479401304094> Minerando...",
            description="Aguarde enquanto você minera recursos!",
            color=discord.Color.blue()
        )
        await interaction.edit_original_response(embed=loading_embed, view=None)

        await self.perform_mining(interaction)

    async def perform_mining(self, interaction):
        user_id = str(interaction.user.id)
        user_inv = inventarios.get(user_id, {})

        picaretas_disponiveis = []
        for nome, qtd in user_inv.items():
            if "picareta" in nome.lower() and (isinstance(qtd, list) and sum(qtd) > 0 or isinstance(qtd, (int, float)) and qtd > 0):
                picaretas_disponiveis.append(nome.lower())

        if not picaretas_disponiveis:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você precisa de uma **Picareta** para minerar!", ephemeral=True)
            return

        nivel_picareta = 0
        if any("diamante" in p or "diamond" in p for p in picaretas_disponiveis):
            nivel_picareta = 5
        elif any("ouro" in p or "gold" in p for p in picaretas_disponiveis):
            nivel_picareta = 4
        elif any("ferro" in p or "iron" in p for p in picaretas_disponiveis):
            nivel_picareta = 3
        elif any("pedra" in p or "stone" in p for p in picaretas_disponiveis):
            nivel_picareta = 2
        elif any("madeira" in p or "wood" in p for p in picaretas_disponiveis):
            nivel_picareta = 1

        qtd_ouro_bruto = 0
        qtd_diamante_bruto = 0

        if nivel_picareta >= 4:
            qtd_pedregulho = random.randint(2, 20)

            qtd_carvao = 0
            if random.random() < 0.5:
                qtd_carvao = random.randint(1, 37)

            qtd_ferro_bruto = 0
            if random.random() < 0.4:
                qtd_ferro_bruto = random.randint(1, 13)

            if random.random() < 0.3:
                qtd_ouro_bruto = random.randint(1, 10)

            if random.random() < 0.06:
                qtd_diamante_bruto = random.randint(1, 8)
        elif nivel_picareta == 3:
            qtd_pedregulho = random.randint(1, 18)
            qtd_carvao = random.randint(1, 20)

            qtd_ferro_bruto = 0
            if random.random() < 0.4:
                qtd_ferro_bruto = random.randint(1, 13)
        elif nivel_picareta == 2:
            qtd_pedregulho = random.randint(1, 16)
            qtd_carvao = random.randint(1, 18)

            qtd_ferro_bruto = 0
            if random.random() < 0.3:
                qtd_ferro_bruto = random.randint(1, 10)

        if nivel_picareta >= 2:
            qtd_real_pedregulho = adicionar_item(user_id, "Pedregulho", qtd_pedregulho)
            adicionar_blocos_quebrados(user_id, qtd_real_pedregulho)

            qtd_real_carvao = adicionar_item(user_id, "Carvão", qtd_carvao)

            qtd_real_ferro = adicionar_item(user_id, "ferro_bruto", qtd_ferro_bruto) if qtd_ferro_bruto > 0 else 0

            qtd_real_ouro = 0
            if nivel_picareta >= 4 and qtd_ouro_bruto > 0:
                qtd_real_ouro = adicionar_item(user_id, "ouro_bruto", qtd_ouro_bruto)

            qtd_real_diamante = 0
            if qtd_diamante_bruto > 0:
                qtd_real_diamante = adicionar_item(user_id, "diamante", qtd_diamante_bruto)

            mensagem_limite = ""
            limite_items = []
            if qtd_real_pedregulho < qtd_pedregulho:
                limite_items.append("Pedregulho")
            if qtd_real_carvao < qtd_carvao:
                limite_items.append("Carvão")
            if qtd_ferro_bruto > 0 and qtd_real_ferro < qtd_ferro_bruto:
                limite_items.append("Ferro Bruto")
            if qtd_ouro_bruto > 0 and qtd_real_ouro < qtd_ouro_bruto:
                limite_items.append("Ouro Bruto")
            if qtd_diamante_bruto > 0 and qtd_real_diamante < qtd_diamante_bruto:
                limite_items.append("Diamante")

            if limite_items:
                mensagem_limite = f"\n⚠️ {', '.join(limite_items)} atingiram o limite de 64 no inventário!"

            desc_parts = [
                f"<:pedregulho:1391151677930868880> Pedregulho: {qtd_real_pedregulho}"
            ]
            if qtd_real_carvao > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['Carvão']} Carvão: {qtd_real_carvao}")
            if qtd_real_ferro > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['ferro_bruto']} Ferro Bruto: {qtd_real_ferro}")
            if qtd_real_ouro > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['ouro_bruto']} Ouro Bruto: {qtd_real_ouro}")
            if qtd_real_diamante > 0:
                desc_parts.append(f"{EMOJIS_MINERIOS['diamante']} Diamante: {qtd_real_diamante}")

            embed = discord.Embed(
                title="<:picaretaferro:1401450479401304094> Mineração realizada!",
                description=f"Você minerou e encontrou:\n" + "\n".join(desc_parts) + mensagem_limite,
                color=discord.Color.dark_gray()
            )
        else:
            qtd_pedregulho = random.randint(1, 18)
            qtd_carvao = random.randint(1, 15)

            qtd_real_pedregulho = adicionar_item(user_id, "Pedregulho", qtd_pedregulho)
            adicionar_blocos_quebrados(user_id, qtd_real_pedregulho)

            qtd_real_carvao = adicionar_item(user_id, "Carvão", qtd_carvao)

            mensagem_limite = ""
            if qtd_real_pedregulho < qtd_pedregulho or qtd_real_carvao < qtd_carvao:
                mensagem_limite = "\n⚠️ Alguns itens atingiram o limite de 64 no inventário!"

            embed = discord.Embed(
                title="<:picaretaferro:1401450479401304094> Mineração realizada!",
                description=f"Você minerou e encontrou:\n<:pedregulho:1391151677930868880> Pedregulho: {qtd_real_pedregulho}\n{EMOJIS_MINERIOS['Carvão']} Carvão: {qtd_real_carvao}{mensagem_limite}",
                color=discord.Color.dark_gray()
            )
        embed.set_image(url="https://minecraft.wiki/images/8/8c/Cave.png")
        embed.set_footer(text="Use sua picareta para encontrar recursos valiosos!")

        def get_total_quantity(value):
            if isinstance(value, list):
                return sum(value)
            else:
                return value

        has_pickaxe_left = any(get_total_quantity(qtd) > 0 for nome, qtd in user_inv.items() if "picareta" in nome.lower())

        if has_pickaxe_left:
            await interaction.edit_original_response(
                embed=embed,
                view=MineracaoResultViewPerfil(self.user_id)
            )
        else:
            await interaction.edit_original_response(
                embed=embed,
                view=None
            )

class EscolherPlantioView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="🌾 Trigo", style=discord.ButtonStyle.secondary, emoji="🌾")
    async def plantar_trigo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        if user_inv.get("sementes", 0) <= 0:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem sementes para plantar!", ephemeral=True)
            return

        user_inv["sementes"] -= 1

        plantacoes = user_inv.setdefault("plantacoes", {})
        plantacao_id = f"trigo_{int(time.time())}"
        plantacoes[plantacao_id] = {
            "tipo": "trigo",
            "tempo_plantio": time.time(),
            "tempo_crescimento": 300,
            "pronto": False
        }

        salvar_inventarios()

        embed = discord.Embed(
            title="🌱 Plantio Realizado!",
            description="Você plantou sementes de trigo!",
            color=discord.Color.green()
        )
        embed.add_field(name="⏰ Tempo para crescer", value="5 minutos", inline=False)
        embed.add_field(name="📦 Sementes restantes", value=f"{user_inv.get('sementes', 0)}", inline=True)
        embed.set_footer(text="Use o botão 🌾 Colher depois que crescer!")

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

    @discord.ui.button(label="🥕 Cenoura", style=discord.ButtonStyle.secondary, emoji="🥕")
    async def plantar_cenoura(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        if user_inv.get("sementes", 0) <= 0:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem sementes para plantar!", ephemeral=True)
            return

        user_inv["sementes"] -= 1

        plantacoes = user_inv.setdefault("plantacoes", {})
        plantacao_id = f"cenoura_{int(time.time())}"
        plantacoes[plantacao_id] = {
            "tipo": "cenoura",
            "tempo_plantio": time.time(),
            "tempo_crescimento": 180,
            "pronto": False
        }

        salvar_inventarios()

        embed = discord.Embed(
            title="🌱 Plantio Realizado!",
            description="Você plantou sementes de cenoura!",
            color=discord.Color.orange()
        )
        embed.add_field(name="⏰ Tempo para crescer", value="3 minutos", inline=False)
        embed.add_field(name="📦 Sementes restantes", value=f"{user_inv.get('sementes', 0)}", inline=True)
        embed.set_footer(text="Use o botão 🌾 Colher depois que crescer!")

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar_plantio(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Isso não é para você!", ephemeral=True)
            return
        await interaction.response.edit_message(content=f"{EMOJIS['c_negativo']} Plantio cancelado.", view=None)

class PlantacaoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="Plantar", emoji="<:enxadaferro:1401450381292081212>", style=discord.ButtonStyle.secondary)
    async def plantar_novo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        def get_total(qtd):
            if isinstance(qtd, list):
                return sum(qtd)
            else:
                return qtd

        tem_enxada = any(get_total(qtd) > 0 for nome, qtd in user_inv.items() if "enxada" in nome.lower())
        if not tem_enxada:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você precisa de uma **Enxada** (qualquer tipo) para plantar!", ephemeral=True)
            return

        plantacao = user_inv.get("plantacao_ativa", None)
        if plantacao:
            tempo_atual = datetime.now().timestamp()
            tempo_restante = plantacao["tempo_colheita"] - tempo_atual

            if tempo_restante > 0:
                horas = int(tempo_restante // 3600)
                minutos = int((tempo_restante % 3600) // 60)
                await interaction.response.send_message(
                    f"{EMOJIS['c_negativo']} Você já tem uma plantação ativa!\n⏰ Tempo restante: {horas}h {minutos}m",
                    ephemeral=True
                )
                return

        sementes_disponiveis = []
        if user_inv.get("sementes_trigo", 0) > 0:
            sementes_disponiveis.append("trigo")

        if not sementes_disponiveis:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem sementes para plantar! Use **Coletar Sementes** primeiro.", ephemeral=True)
            return

        await interaction.response.send_message(
            "🌱 **Escolha o que você quer plantar:**",
            view=EscolherSementeView(self.user_id, sementes_disponiveis),
            ephemeral=True
        )

    @discord.ui.button(label="Colher", emoji="<:paferro:1401450876299645052>", style=discord.ButtonStyle.secondary)
    async def colher_plantacao(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        plantacao = user_inv.get("plantacao_ativa", None)
        if not plantacao:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem nenhuma plantação ativa!", ephemeral=True)
            return

        tempo_atual = datetime.now().timestamp()
        tempo_restante = plantacao["tempo_colheita"] - tempo_atual

        if tempo_restante > 0:
            horas = int(tempo_restante // 3600)
            minutos = int((tempo_restante % 3600) // 60)
            await interaction.response.send_message(
                f"{EMOJIS['c_negativo']} Sua plantação ainda não está pronta!\n⏰ Tempo restante: {horas}h {minutos}m",
                ephemeral=True
            )
            return

        tipo = plantacao["tipo"]
        quantidade = random.randint(2, 4)

        emoji = ""
        sementes_extras = 0
        if tipo == "trigo":
            user_inv["trigo"] = user_inv.get("trigo", 0) + quantidade
            sementes_extras = random.randint(1, 3)
            user_inv["sementes_trigo"] = user_inv.get("sementes_trigo", 0) + sementes_extras
            emoji = "<:trigo:1410991160272617493>"

        del user_inv["plantacao_ativa"]

        from cogs.notificacoes import Notificacoes
        notificacao_cog = interaction.client.get_cog('Notificacoes')
        if notificacao_cog and str(interaction.user.id) in notificacao_cog.usuarios_notificados:
            notificacao_cog.usuarios_notificados.discard(str(interaction.user.id))

        salvar_inventarios()

        embed = discord.Embed(
            title="🎉 Colheita Realizada!",
            description=f"Você colheu sua plantação de **{tipo}**!",
            color=discord.Color.gold()
        )
        embed.add_field(name=f"{emoji} {tipo.title()}", value=f"+{quantidade}", inline=True)
        if sementes_extras > 0:
            embed.add_field(name="<:semente:1395853662277992458> Semente", value=f"+{sementes_extras}", inline=True)

        embed.set_image(url="https://minecraft.wiki/images/2/29/Wheat_Age_7.png")
        embed.set_footer(text="Plante novamente quando quiser!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Soletar Sementes", emoji="<:semente:1395853662277992458>", style=discord.ButtonStyle.secondary)
    async def coletar_sementes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não pode usar esse botão.", ephemeral=True)
            return

        user_inv = inventarios.setdefault(str(interaction.user.id), {})

        def get_total(qtd):
            if isinstance(qtd, list):
                return sum(qtd)
            else:
                return qtd

        tem_pa = any(get_total(qtd) > 0 for nome, qtd in user_inv.items() if "pa" in nome.lower() or "pá" in nome.lower())
        if not tem_pa:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você precisa de uma **Pá** (qualquer tipo) para coletar sementes!", ephemeral=True)
            return

        sementes_obtidas = 5
        quantidade_trigo = 2

        user_inv["sementes_trigo"] = user_inv.get("sementes_trigo", 0) + sementes_obtidas

        from utils.database import adicionar_xp
        xp_info = adicionar_xp(interaction.user.id, quantidade_trigo)

        salvar_inventarios()

        embed = discord.Embed(
            title="<:semente:1395853662277992458> Sementes Coletadas!",
            description=f"Você usou sua **Pá** para coletar sementes!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📦 Resultado",
            value=f"<:semente:1395853662277992458> Sementes obtidas: {sementes_obtidas}\n⭐ XP ganho: +{xp_info['xp_ganho']}",
            inline=False
        )

        if xp_info['subiu_nivel']:
            embed.add_field(
                name="🎉 Level Up!",
                value=f"Você chegou ao nível {xp_info['nivel_atual']}!",
                inline=False
            )

        embed.set_image(url="https://minecraft.wiki/images/7/78/Wheat_Seeds_JE2_BE2.png")
        embed.set_footer(text="Use as sementes para plantar mais trigo!")

        await interaction.response.send_message(embed=embed, ephemeral=True)
