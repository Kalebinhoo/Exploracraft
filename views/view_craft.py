import discord
from discord.ui import View, Select
from views.itens_crafting import ITENS_CRAFTING
from icons.emojis import EMOJIS
from icons.emojis_minerios import EMOJIS_MINERIOS
from icons.emojis_blocos import EMOJIS_BLOCOS
from icons.emojis_itens import EMOJIS_ITENS
from icons.emojis_comidas import EMOJIS_COMIDAS
from utils.conquistas_data import completar_conquista

def get_item_emoji(item_name):
    """Retorna o emoji correspondente ao item usando apenas emojis customizados"""
    item_lower = item_name.lower()
    
    if item_lower in EMOJIS_ITENS:
        return EMOJIS_ITENS[item_lower]
    
    if item_lower in EMOJIS_MINERIOS:
        return EMOJIS_MINERIOS[item_lower]
    
    if item_lower in EMOJIS_BLOCOS:
        return EMOJIS_BLOCOS[item_lower]
        
    if item_lower in EMOJIS_COMIDAS:
        return EMOJIS_COMIDAS[item_lower]
    
    if item_lower in EMOJIS:
        return EMOJIS[item_lower]
    
    emoji_map = {
        "tábua de carvalho": EMOJIS_BLOCOS.get("tabua de carvalho", "🪵"),
        "tábua": EMOJIS_BLOCOS.get("tabua de carvalho", "🪵"),
        "barra de ferro": EMOJIS_MINERIOS.get("barradeferro", "🔶"),
        "ferro bruto": EMOJIS_MINERIOS.get("ferro_bruto", "🔶"),
        "barra de ouro": EMOJIS_MINERIOS.get("barradeouro", "💰"),
        "ouro bruto": EMOJIS_MINERIOS.get("ouro_bruto", "💰"),
        "carvão": EMOJIS_MINERIOS.get("Carvão", "⚫"),
        "lã": "🐑",
        "leite": "🥛",
        "ovo": "🥚",
        "açúcar": "🍯",
    }
    
    return emoji_map.get(item_lower, "📦")

class CategoriaDropdown(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        category_emojis = {
            "Blocos": EMOJIS.get('bloco de grama', ''),
            "Enxadas": EMOJIS.get('enxada de ferro', ''),
            "Espadas": EMOJIS.get('espada de ferro', ''),
            "Itens": EMOJIS.get('cama', ''),
            "Machados": EMOJIS.get('machado de ferro', ''),
            "Picaretas": EMOJIS.get('picareta de ferro', ''),
            "Pás": EMOJIS.get('pá de ferro', '')
        }
        options = [
            discord.SelectOption(
                label=categoria,
                description=f"Itens da categoria {categoria.lower()}",
                emoji=category_emojis.get(categoria, None)
            )
            for categoria in ITENS_CRAFTING.keys()
        ]
        super().__init__(
            placeholder="Escolha uma categoria de crafting...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        itens = ITENS_CRAFTING.get(categoria, [])

        embed = discord.Embed(
            title=f"📦 Itens em: {categoria}",
            description="Selecione um item para craftar.",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=embed, view=ItemDropdownView(self.user_id, categoria))

class ItemDropdown(discord.ui.Select):
    def __init__(self, user_id, categoria):
        self.user_id = user_id
        self.categoria = categoria
        itens = ITENS_CRAFTING.get(categoria, [])
        options = []
        def normalize_item_name(name):
            name_map = {
                "Tábua de Carvalho": "tabua de carvalho",
                "Tábua de Abeto": "tabua de abeto",
                "Tábua de Acácia": "tabua de acacia",
                "Tábua de Bétula": "tabua de betula",
                "Tábua de Carvalho Escuro": "tabua de carvalho escuro",
                "Tábua de Cerejeira": "tabua de cerejeira",
                "Tábua de Selva": "tabua de selva",
                "Tábua de Mangue": "tabua de mangue",
                "Picareta de Madeira": "picareta de madeira",
                "Picareta de Pedra": "picareta de pedra",
                "Picareta de Ferro": "picareta de ferro",
                "Espada de Madeira": "espada de madeira",
                "Espada de Pedra": "espada de pedra",
                "Espada de Ferro": "espada de ferro",
                "Pá de Madeira": "pá de madeira",
                "Pá de Pedra": "pá de pedra",
                "Pá de Ferro": "pá de ferro",
                "Machado de Madeira": "machado de madeira",
                "Machado de Pedra": "machado de pedra",
                "Machado de Ferro": "machado de ferro",
                "Enxada de Madeira": "enxada de madeira",
                "Enxada de Pedra": "enxada de pedra",
                "Enxada de Ferro": "enxada de ferro",
                "Graveto": "graveto",
                "Fornalha": "fornalha",
                "Cama": "cama",
                "Báu": "bau",
                "Suporte de Poções": "suporte de poções",
                "Pão": "pão",
                "Pederneira": "pederneira"
            }
            return name_map.get(name, name.lower())

        for item in itens:
            nome = item["nome"]
            nome_normalizado = normalize_item_name(nome)
            emoji = EMOJIS.get(nome_normalizado, "")
            options.append(discord.SelectOption(
                label=nome,
                description=None,
                emoji=emoji if emoji else None
            ))
        super().__init__(
            placeholder="Escolha um item para craftar...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        import unicodedata
        def normalizar(nome):
            return unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII').lower()

        item_nome = self.values[0]
        from views.receitas_craft import RECEITAS_CRAFT
        from utils.database import inventarios, salvar_inventarios, adicionar_item

        user_id = str(interaction.user.id)
        user_inv = inventarios.setdefault(user_id, {})
        receita = RECEITAS_CRAFT.get(item_nome)

        if not receita:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Não existe receita cadastrada para **{item_nome}**.", ephemeral=True)
            return

        if item_nome == "Graveto":
            def get_total_quantity(value):
                if isinstance(value, list):
                    return sum(value)
                else:
                    return value

            plank_found = False
            for k, v in list(user_inv.items()):
                if normalizar(k).startswith("tabua"):
                    total = get_total_quantity(v)
                    if total >= 2:
                        plank_found = True
                        stacks = user_inv[k]
                        if not isinstance(stacks, list):
                            stacks = [stacks] if stacks > 0 else []
                        remaining = 2
                        for i in range(len(stacks) - 1, -1, -1):
                            if stacks[i] >= remaining:
                                stacks[i] -= remaining
                                remaining = 0
                                break
                            else:
                                remaining -= stacks[i]
                                stacks[i] = 0
                        stacks = [s for s in stacks if s > 0]
                        if stacks:
                            user_inv[k] = stacks
                        else:
                            del user_inv[k]
                        break
            if not plank_found:
                emoji_tabua = get_item_emoji("Tábua de Carvalho")
                await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem os itens necessários para craftar **{item_nome}**:\n{emoji_tabua} Tábua (2)", ephemeral=True)
                return
            quantidade_craftada = 4
            adicionar_item(user_id, item_nome, quantidade_craftada)
            embed = discord.Embed(
                title=f"✅ Crafting realizado!",
                description=f"Você criou **{quantidade_craftada}x {item_nome}** com sucesso!\n\nVocê pode continuar craftando outros itens da mesma categoria.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(
                embed=embed,
                view=ItemDropdownView(self.user_id, self.categoria)
            )
            return

        if item_nome == "Báu":
            def get_total_quantity(value):
                if isinstance(value, list):
                    return sum(value)
                else:
                    return value

            total_planks_needed = 8
            planks_consumed = 0
            for k, v in list(user_inv.items()):
                if normalizar(k).startswith("tabua"):
                    total = get_total_quantity(v)
                    if total > 0:
                        consume = min(total, total_planks_needed - planks_consumed)
                        planks_consumed += consume
                        stacks = user_inv[k]
                        if not isinstance(stacks, list):
                            stacks = [stacks] if stacks > 0 else []
                        remaining = consume
                        for i in range(len(stacks) - 1, -1, -1):
                            if stacks[i] >= remaining:
                                stacks[i] -= remaining
                                remaining = 0
                                break
                            else:
                                remaining -= stacks[i]
                                stacks[i] = 0
                        stacks = [s for s in stacks if s > 0]
                        if stacks:
                            user_inv[k] = stacks
                        else:
                            del user_inv[k]
                        if planks_consumed >= total_planks_needed:
                            break
            if planks_consumed < total_planks_needed:
                emoji_tabua = get_item_emoji("Tábua de Carvalho")
                await interaction.response.send_message(f"{EMOJIS['c_negativo']} Você não tem os itens necessários para craftar **{item_nome}**:\n{emoji_tabua} Tábua (8)", ephemeral=True)
                return
            quantidade_craftada = 1
            adicionar_item(user_id, item_nome, quantidade_craftada)
            embed = discord.Embed(
                title=f"✅ Crafting realizado!",
                description=f"Você criou **{quantidade_craftada}x {item_nome}** com sucesso!\n\nVocê pode continuar craftando outros itens da mesma categoria.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(
                embed=embed,
                view=ItemDropdownView(self.user_id, self.categoria)
            )
            return

        inv_normalizado = {normalizar(k): v for k, v in user_inv.items()}

        def get_total_quantity(value):
            if isinstance(value, list):
                return sum(value)
            else:
                return value

        faltando = []
        for ingrediente, qtd in receita.items():
            if ingrediente == "Tábua de Carvalho":
                total_planks = sum(get_total_quantity(v) for k, v in user_inv.items() if normalizar(k).startswith("tabua"))
                if total_planks < qtd:
                    emoji = get_item_emoji("Tábua de Carvalho")
                    faltando.append(f"{emoji} Tábua ({qtd})")
            elif ingrediente == "Barra de Ferro":
                total_ferro = get_total_quantity(inv_normalizado.get("barradeferro", 0)) + get_total_quantity(inv_normalizado.get("barra_ferro", 0))
                if total_ferro < qtd:
                    emoji = get_item_emoji("Barra de Ferro")
                    faltando.append(f"{emoji} {ingrediente} ({qtd})")
            else:
                ingrediente_norm = normalizar(ingrediente)
                total_qty = get_total_quantity(inv_normalizado.get(ingrediente_norm, 0))
                if total_qty < qtd:
                    emoji = get_item_emoji(ingrediente)
                    faltando.append(f"{emoji} {ingrediente} ({qtd})")

        if faltando:
            await interaction.response.send_message(
                f"{EMOJIS['c_negativo']} Você não tem os itens necessários para craftar **{item_nome}**:\n" + "\n".join(faltando),
                ephemeral=True
            )
            return

        for ingrediente, qtd in receita.items():
            if ingrediente == "Tábua de Carvalho":
                planks_to_consume = qtd
                for k in list(user_inv.keys()):
                    if normalizar(k).startswith("tabua"):
                        stacks = user_inv[k]
                        if not isinstance(stacks, list):
                            stacks = [stacks] if stacks > 0 else []
                        for i in range(len(stacks) - 1, -1, -1):
                            if stacks[i] > 0:
                                consume = min(stacks[i], planks_to_consume)
                                stacks[i] -= consume
                                planks_to_consume -= consume
                                if planks_to_consume <= 0:
                                    break
                        stacks = [s for s in stacks if s > 0]
                        if stacks:
                            user_inv[k] = stacks
                        else:
                            del user_inv[k]
                        if planks_to_consume <= 0:
                            break
            elif ingrediente == "Barra de Ferro":
                remaining = qtd
                nome_real = next((k for k in user_inv if normalizar(k) == "barradeferro"), None)
                if nome_real:
                    stacks = user_inv.get(nome_real, [])
                    if not isinstance(stacks, list):
                        stacks = [stacks] if stacks > 0 else []
                    for i in range(len(stacks) - 1, -1, -1):
                        if stacks[i] >= remaining:
                            stacks[i] -= remaining
                            remaining = 0
                            break
                        else:
                            remaining -= stacks[i]
                            stacks[i] = 0
                    stacks = [s for s in stacks if s > 0]
                    if stacks:
                        user_inv[nome_real] = stacks
                    else:
                        if nome_real in user_inv:
                            del user_inv[nome_real]

                if remaining > 0:
                    nome_real = next((k for k in user_inv if normalizar(k) == "barra_ferro"), None)
                    if nome_real:
                        stacks = user_inv.get(nome_real, [])
                        if not isinstance(stacks, list):
                            stacks = [stacks] if stacks > 0 else []
                        for i in range(len(stacks) - 1, -1, -1):
                            if stacks[i] >= remaining:
                                stacks[i] -= remaining
                                remaining = 0
                                break
                            else:
                                remaining -= stacks[i]
                                stacks[i] = 0
                        stacks = [s for s in stacks if s > 0]
                        if stacks:
                            user_inv[nome_real] = stacks
                        else:
                            if nome_real in user_inv:
                                del user_inv[nome_real]
            else:
                ingrediente_norm = normalizar(ingrediente)
                nome_real = next((k for k in user_inv if normalizar(k) == ingrediente_norm), ingrediente)
                stacks = user_inv.get(nome_real, [])
                if not isinstance(stacks, list):
                    stacks = [stacks] if stacks > 0 else []
                remaining = qtd
                for i in range(len(stacks) - 1, -1, -1):
                    if stacks[i] >= remaining:
                        stacks[i] -= remaining
                        remaining = 0
                        break
                    else:
                        remaining -= stacks[i]
                        stacks[i] = 0
                stacks = [s for s in stacks if s > 0]
                if stacks:
                    user_inv[nome_real] = stacks
                else:
                    if nome_real in user_inv:
                        del user_inv[nome_real]
        if normalizar(item_nome) == normalizar("Graveto"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Carvalho"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Abeto"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Acácia"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Bétula"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Carvalho Escuro"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Cerejeira"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Selva"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Tábua de Mangue"):
            quantidade_craftada = 4
        elif normalizar(item_nome) == normalizar("Báu"):
            quantidade_craftada = 1
        else:
            quantidade_craftada = 1
        adicionar_item(user_id, item_nome, quantidade_craftada)

        if normalizar(item_nome).startswith("picareta"):
            completar_conquista(user_id, "time_to_mine", interaction.client)

        if normalizar(item_nome).startswith("enxada"):
            completar_conquista(user_id, "time_to_farm", interaction.client)

        if normalizar(item_nome) == "fornalha":
            completar_conquista(user_id, "hot_topic", interaction.client)

        if normalizar(item_nome) == "bolo":
            completar_conquista(user_id, "the_lie", interaction.client)

        if normalizar(item_nome) == "pão":
            completar_conquista(user_id, "bake_bread", interaction.client)

        if normalizar(item_nome).startswith("picareta"):
            hierarquia_picaretas = [
                "Picareta de Madeira",
                "Picareta de Pedra",
                "Picareta de Ferro",
                "Picareta de Ouro",
                "Picareta de Diamante"
            ]

            try:
                indice_craftada = hierarquia_picaretas.index(item_nome)
                if indice_craftada >= 1:
                    completar_conquista(user_id, "getting_an_upgrade", interaction.client)
                for i in range(indice_craftada):
                    picareta_inferior = hierarquia_picaretas[i]
                    if picareta_inferior in user_inv:
                        del user_inv[picareta_inferior]
            except ValueError:
                pass

        embed = discord.Embed(
            title=f"✅ Crafting realizado!",
            description=f"Você criou **{quantidade_craftada}x {item_nome}** com sucesso!\n\nVocê pode continuar craftando outros itens da mesma categoria.",
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=ItemDropdownView(self.user_id, self.categoria)
        )

class VoltarButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="⬅️ Voltar", style=discord.ButtonStyle.secondary)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['c_negativo']} Esse botão não é seu!", ephemeral=True)
            return
        embed = discord.Embed(
            title="🛠️ Sistema de Crafting",
            description="Escolha uma categoria de crafting...",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=embed, view=CategoriaDropdownView(self.user_id))

class ItemDropdownView(View):
    def __init__(self, user_id, categoria):
        super().__init__(timeout=None)
        self.add_item(ItemDropdown(user_id, categoria))
        self.add_item(VoltarButton(user_id))

class CategoriaDropdownView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.add_item(CategoriaDropdown(user_id))

