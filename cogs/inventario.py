import discord
from discord import app_commands
from discord.ext import commands
from utils.database import inventarios, salvar_inventarios, contar_slots_inventario
from icons.emojis import EMOJIS
from icons.emojis_icones import EMOJIS_ICONES
from utils.conquistas_data import completar_conquista

TOOLS = [
    "machado de madeira", "machado de ferro", "machado de ouro", "machado de pedra", "machado de diamante",
    "espada de madeira", "espada de ferro", "espada de ouro", "espada de pedra", "espada de diamante",
    "arco",
    "picareta de madeira", "picareta de ferro", "picareta de ouro", "picareta de pedra", "picareta de diamante",
    "pá de madeira", "pá de ferro", "pá de ouro", "pá de pedra", "pá de diamante"
]

class DescarteModal(discord.ui.Modal):
    def __init__(self, valid_items):
        super().__init__(title="Descartar Item")
        self.valid_items = valid_items

    item_num = discord.ui.TextInput(
        label="Número do Item",
        placeholder="Digite o número do item na lista (ex: 1)",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            num = int(self.item_num.value.strip())
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Número inválido.", ephemeral=True)
            return

        if num < 1 or num > len(self.valid_items):
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Número fora do intervalo. Use 1 a {len(self.valid_items)}.", ephemeral=True)
            return

        item_data, qtd, display_name, emoji = self.valid_items[num - 1]

        user_id = str(interaction.user.id)

        user_inv = inventarios[user_id]
        if isinstance(item_data, tuple):
            item, stack_idx = item_data
            stacks = user_inv.get(item, [])
            if isinstance(stacks, list) and 0 <= stack_idx < len(stacks):
                del stacks[stack_idx]
                if not stacks:
                    del user_inv[item]
                else:
                    user_inv[item] = stacks
                salvar_inventarios()

        await interaction.response.send_message(f"{EMOJIS_ICONES['baldedelava']} Você descartou **{qtd}x** `{display_name}` do seu inventário!", ephemeral=True)

class DroparModal(discord.ui.Modal):
    def __init__(self, valid_items):
        super().__init__(title="Dropar Item")
        self.valid_items = valid_items

    item_num = discord.ui.TextInput(
        label="Número do Item",
        placeholder="Digite o número do item na lista (ex: 1)",
        required=True,
        max_length=10
    )

    quantidade = discord.ui.TextInput(
        label="Quantidade",
        placeholder="Digite a quantidade a dropar",
        required=True,
        max_length=10
    )

    user_id = discord.ui.TextInput(
        label="ID do Usuário",
        placeholder="Digite o ID do usuário destinatário",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            num = int(self.item_num.value.strip())
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Número do item inválido.", ephemeral=True)
            return

        if num < 1 or num > len(self.valid_items):
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Número fora do intervalo. Use 1 a {len(self.valid_items)}.", ephemeral=True)
            return

        try:
            qtd = int(self.quantidade.value.strip())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Quantidade inválida.", ephemeral=True)
            return

        try:
            dest_id = str(int(self.user_id.value.strip()))
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} ID do usuário inválido.", ephemeral=True)
            return

        item_data, qtd_disp, display_name, emoji = self.valid_items[num - 1]

        user_id = str(interaction.user.id)

        if qtd > qtd_disp:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem **{qtd}x** `{display_name}` para dropar.", ephemeral=True)
            return

        user_inv = inventarios[user_id]
        dest_inv = inventarios.setdefault(dest_id, [])

        if isinstance(item_data, tuple):
            item, stack_idx = item_data
            stacks = user_inv.get(item, [])
            dest_stacks = dest_inv.get(item, [])
            if not isinstance(dest_stacks, list):
                dest_stacks = [dest_stacks] if dest_stacks > 0 else []
            if isinstance(stacks, list) and 0 <= stack_idx < len(stacks) and stacks[stack_idx] >= qtd:
                stacks[stack_idx] -= qtd
                for i in range(len(dest_stacks)):
                    if dest_stacks[i] < 64:
                        can_add = min(qtd, 64 - dest_stacks[i])
                        dest_stacks[i] += can_add
                        qtd -= can_add
                        if qtd <= 0:
                            break
                while qtd > 0:
                    can_add = min(qtd, 64)
                    dest_stacks.append(can_add)
                    qtd -= can_add

                stacks = [s for s in stacks if s > 0]
                dest_stacks = [s for s in dest_stacks if s > 0]

                if stacks:
                    user_inv[item] = stacks
                else:
                    if item in user_inv:
                        del user_inv[item]

                if dest_stacks:
                    dest_inv[item] = dest_stacks
                else:
                    if item in dest_inv:
                        del dest_inv[item]

                salvar_inventarios()

            try:
                user = await interaction.client.fetch_user(int(dest_id))
                mention = user.mention
            except:
                mention = f"Usuário {dest_id}"

            await interaction.response.send_message(f"<a:bauabrindo:1419310349391237222> Você dropou **{qtd}x** `{display_name}` para {mention}!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Erro ao dropar o item.", ephemeral=True)

class InventarioView(discord.ui.View):
    def __init__(self, pages, valid_items, user_name, total_slots, user_id):
        super().__init__(timeout=None)
        self.pages = pages
        self.valid_items = valid_items
        self.user_name = user_name
        self.total_slots = total_slots
        self.user_id = user_id
        self.current_page = 0

    def get_embed(self):
        crafting_emoji = EMOJIS.get("crafting", "")
        if not self.pages:
            desc = "📦 Seu inventário está vazio."
        else:
            desc = "\n".join(self.pages[self.current_page])
            if self.current_page == len(self.pages) - 1 and self.user_id != "1324198892648009760" and self.total_slots >= 30:
                aviso = f"\n\n⚠️ **Atenção:** Seu inventário está ficando cheio! ({self.total_slots}/36 slots ocupados)"
                desc += aviso
        embed = discord.Embed(
            title=f"{crafting_emoji} Inventário de {self.user_name}",
            description=desc,
            color=discord.Color.orange()
        )
        return embed

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Descartar", style=discord.ButtonStyle.danger, emoji=EMOJIS_ICONES["baldedelava"])
    async def descarte_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DescarteModal(self.valid_items))

    @discord.ui.button(label="Dropar", style=discord.ButtonStyle.secondary, emoji="<a:bauabrindo:1419310349391237222>")
    async def dropar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DroparModal(self.valid_items))

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def normalizar_nome(self, nome):
        """Normaliza o nome do item para buscar o emoji correspondente"""
        import unicodedata
        nome = unicodedata.normalize('NFKD', str(nome)).encode('ASCII', 'ignore').decode('ASCII')
        nome = nome.replace('_', ' ').lower()
        return nome

    @app_commands.command(name="inventario", description="Veja seus itens coletados")
    async def inventario(self, interaction: discord.Interaction):
        from utils.database import is_registered

        await interaction.response.defer(ephemeral=True)

        try:
            user_id = str(interaction.user.id)

            if not is_registered(user_id):
                await interaction.followup.send(f"{EMOJIS['c_negativo']} Você precisa usar `/iniciar` antes de ver seu inventário!", ephemeral=True)
                return

            user_inv = inventarios.get(user_id, {})

            campos_especiais = [
                "bioma_atual", "vida", "fome", "xp", "nivel",
                "plantacao_ativa", "registrado", "animais_disponiveis",
                "recursos_disponiveis"
            ]
            valid_items = []
            itens_formatados = []

            emoji_mapping = {
                "bifecrua": "bifecrua",
                "cordeirocrua": "cordeirocrua",
                "frango": "frango",
                "costelacrua": "costelacrua",
                "la": "la",
                "couro": "couro",
                "pena": "pena",
                "sementes_trigo": "semente",
                "frangocrua": "frango",
                "costlacrua": "costelacrua",
                "bifeassado": "bifeassado",
                "cordeiroassado": "cordeiroassado",
                "frangoassado": "frangoassado",
                "costelaassada": "costelaassada",
                "ferro_bruto": "ferrobruto",
                "barradeferro": "barradeferro",
                "pá de madeira": "pá de madeira",
                "pá de ferro": "pá de ferro",
                "pá de ouro": "pá de ouro",
                "pá de pedra": "pá de pedra",
                "pá de diamante": "pá de diamante",
                "pÃ¡ de madeira": "pá de madeira",
                "pÃ¡ de ferro": "pá de ferro",
                "pÃ¡ de ouro": "pá de ouro",
                "pÃ¡ de pedra": "pÃ¡ de pedra",
                "pÃ¡ de diamante": "pÃ¡ de diamante",
                "Ossos": "osso",
                "Flechas": "flecha",
                "botas de couro": "botasdecouro",
                "vara de pesca": "varadepesca",
                "salmão cru": "salmaocru",
                "peixe tropical": "peixetropical",
                "bacalhau cru": "bacalhaucru",
                "fio": "linha"
            }

            name_mapping = {
                "sementes_trigo": "Semente",
                "bifecrua": "bifecrua",
                "cordeirocrua": "cordeirocrua",
                "frango": "frango",
                "costelacrua": "costelacrua",
                "la": "la",
                "couro": "couro",
                "pena": "pena",
                "bifeassado": "bifeassado",
                "cordeiroassado": "cordeiroassado",
                "frangoassado": "frangoassado",
                "costelaassada": "costelaassada",
                "ferro_bruto": "Ferro Bruto",
                "ouro_bruto": "Ouro Bruto",
                "barradeferro": "Barra de Ferro",
                "pá de madeira": "Pá de Madeira",
                "pá de ferro": "Pá de Ferro",
                "pá de ouro": "Pá de Ouro",
                "pá de pedra": "Pá de Pedra",
                "pá de diamante": "Pá de Diamante",
                "pÃ¡ de madeira": "Pá de Madeira",
                "pÃ¡ de ferro": "Pá de Ferro",
                "pÃ¡ de ouro": "Pá de Ouro",
                "pÃ¡ de pedra": "Pá de Pedra",
                "pÃ¡ de diamante": "Pá de Diamante",
                "tronco de cerejeira": "Tronco de Cerejeira",
                "tronco de carvalho": "Tronco de Carvalho",
                "tronco de betula": "Tronco de Betula",
                "tronco de carvalho escuro": "Tronco de Carvalho Escuro",
                "tronco de abeto": "Tronco de Abeto",
                "tronco de selva": "Tronco de Selva",
                "tronco de acacia": "Tronco de Acacia",
                "tronco de mangue": "Tronco de Mangue",
                "botas de couro": "Botas de Couro",
                "vara de pesca": "Vara de Pesca",
                "salmão cru": "Salmão Cru",
                "peixe tropical": "Peixe Tropical",
                "bacalhau cru": "Bacalhau Cru",
                "fio": "Fio",
                "sílex": "Sílex",
                "cascalho": "Cascalho"
            }

            for item, qtd in user_inv.items():
                if item in campos_especiais:
                    continue

                if isinstance(qtd, list):
                    stacks = qtd
                elif isinstance(qtd, (int, float)) and qtd > 0:
                    stacks = [qtd]
                else:
                    continue

                for stack_idx, stack_qtd in enumerate(stacks):
                    try:
                        stack_qtd = float(stack_qtd)
                        if stack_qtd <= 0:
                            continue
                    except (ValueError, TypeError):
                        continue

                    emoji_key = emoji_mapping.get(item)
                    if emoji_key and emoji_key in EMOJIS:
                        emoji = EMOJIS[emoji_key]
                    else:
                        chave_emoji = self.normalizar_nome(item)
                        emoji = ""
                        for key in EMOJIS:
                            if self.normalizar_nome(key) == chave_emoji:
                                emoji = EMOJIS[key]
                                break

                    display_name = name_mapping.get(item, item)
                    valid_items.append(((item, stack_idx), int(stack_qtd), display_name, emoji))

            for idx, (item, qtd_num, display_name, emoji) in enumerate(valid_items, 1):
                itens_formatados.append(f"{idx}. {emoji} {display_name}: {qtd_num}")

            items_per_page = 10
            pages = [itens_formatados[i:i + items_per_page] for i in range(0, len(itens_formatados), items_per_page)]

            total_slots = contar_slots_inventario(user_id)
            if user_id != "1324198892648009760":
                if total_slots >= 36:
                    embed_dm = discord.Embed(
                        title="⚠️ Inventário Cheio!",
                        description=f"Seu inventário está completamente cheio (36/36 slots ocupados).\n\n **Instrução de como manter sempre seu inventário limpo e organizado:** \n\n{EMOJIS.get('1', '1.')} **Dicas para manter o inventário organizado:**\n\n{EMOJIS.get('2', '2.')}",
                        color=discord.Color.red()
                    )
                    try:
                        await interaction.user.send(embed=embed_dm)
                    except discord.Forbidden:
                        pass

            crafting_emoji = EMOJIS.get("crafting", "")
            view = InventarioView(pages, valid_items, interaction.user.name, total_slots, user_id)
            embed = view.get_embed()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

            completar_conquista(user_id, "taking_inventory", self.bot)

        except Exception as e:
            await interaction.followup.send(f"{EMOJIS['c_negativo']} Ocorreu um erro ao exibir o inventário: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Inventario(bot))
