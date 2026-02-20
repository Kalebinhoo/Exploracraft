CONQUISTAS = {
    "taking_inventory": {
        "nome": "Fazendo inventário",
        "descricao": "Abra seu inventário",
        "emoji": "📦",
        "tipo": "opened_inventory",
        "requisito": 1
    },
    "getting_wood": {
        "nome": "Apanhando Madeira",
        "descricao": "Soco uma árvore até que saia um bloco de madeira",
        "emoji": "🌳",
        "tipo": "collected_wood",
        "requisito": 1
    },
    "time_to_mine": {
        "nome": "Hora de Minerar!",
        "descricao": "Use tábuas e gravetos para fazer uma picareta",
        "emoji": "⛏️",
        "tipo": "crafted_pickaxe",
        "requisito": 1
    },
    "hot_topic": {
        "nome": "Assunto Quente",
        "descricao": "Faça uma fornalha com oito blocos de pedregulhos",
        "emoji": "🔥",
        "tipo": "crafted_furnace",
        "requisito": 1
    },
    "acquire_hardware": {
        "nome": "Adquirir Ferramentas",
        "descricao": "Funda um lingote de ferro",
        "emoji": "⚙️",
        "tipo": "smelted_iron",
        "requisito": 1
    },
    "time_to_farm": {
        "nome": "Hora de Plantar!",
        "descricao": "Faça uma enxada",
        "emoji": "🌾",
        "tipo": "crafted_hoe",
        "requisito": 1
    },
    "bake_bread": {
        "nome": "Assar Pão",
        "descricao": "Transforme trigo em pão",
        "emoji": "🍞",
        "tipo": "smelted_bread",
        "requisito": 1
    },
    "the_lie": {
        "nome": "A Mentira",
        "descricao": "Faça um bolo usando: trigo, açúcar, leite, e ovos",
        "emoji": "🎂",
        "tipo": "crafted_cake",
        "requisito": 1
    },
    "getting_an_upgrade": {
        "nome": "Aprimorando",
        "descricao": "Construa uma picareta melhor",
        "emoji": "⛏️",
        "tipo": "crafted_better_pickaxe",
        "requisito": 1
    },
    "delicious_fish": {
        "nome": "Pescaria Produtiva",
        "descricao": "Pesque e cozinhe uma peixe!",
        "emoji": "🐟",
        "tipo": "cooked_fish",
        "requisito": 1
    }
}

def verificar_conquista(user_id, conquista_id):
    """Verifica se o jogador completou uma conquista específica."""
    from utils.database import carregar_dados, get_inventario, get_blocos_quebrados
    dados = carregar_dados(user_id)
    conquista = CONQUISTAS.get(conquista_id)

    if not conquista:
        return False

    tipo = conquista["tipo"]

    if tipo == "nivel":
        nivel = dados.get("nivel", 1)
        return nivel >= conquista["requisito"]

    elif tipo == "item":
        inventario = get_inventario(user_id)
        item = conquista["item"]
        quantidade = 0

        if item in inventario:
            stacks = inventario[item]
            if isinstance(stacks, list):
                quantidade = sum(stacks)
            else:
                quantidade = stacks

        return quantidade >= conquista["requisito"]

    elif tipo == "blocos_quebrados":
        blocos = get_blocos_quebrados(user_id)
        return blocos >= conquista["requisito"]

    elif tipo == "crafts":
        return False

    elif tipo == "construcoes":
        inventario = get_inventario(user_id)
        construcoes = sum(1 for item in inventario.keys() if item.startswith("🏗️"))
        return construcoes >= conquista["requisito"]

    elif tipo == "cacadas":
        return False

    elif tipo == "pescas":
        return False

    elif tipo == "biomas":
        return False

    elif tipo == "opened_inventory":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "collected_wood":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "crafted_pickaxe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "crafted_furnace":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "smelted_iron":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "crafted_hoe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "smelted_bread":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "crafted_cake":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "crafted_better_pickaxe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    elif tipo == "cooked_fish":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        return conquista_id in conquistas_completadas

    return False

def get_conquistas_completadas(user_id):
    """Retorna lista de conquistas completadas pelo jogador."""
    completadas = []
    for conquista_id in CONQUISTAS.keys():
        if verificar_conquista(user_id, conquista_id):
            completadas.append(conquista_id)
    return completadas

def completar_conquista(user_id, conquista_id, bot=None):
    """Marca uma conquista como completada, dá recompensa de XP e envia DM se for a primeira vez."""
    from utils.database import carregar_dados, salvar_dados, adicionar_xp
    dados = carregar_dados(user_id)
    conquistas_completadas = dados.get("conquistas_completadas", [])

    if conquista_id not in conquistas_completadas:
        conquistas_completadas.append(conquista_id)
        dados["conquistas_completadas"] = conquistas_completadas
        salvar_dados(user_id, dados)

        adicionar_xp(user_id, 50)

        if bot:
            import discord
            try:
                user = bot.get_user(int(user_id))
                if user:
                    conquista = CONQUISTAS.get(conquista_id)
                    thumbnails = {
                        "taking_inventory": "https://minecraft.wiki/images/AchievementSprite_taking-inventory.png?11e3b",
                        "getting_wood": "https://minecraft.wiki/images/AchievementSprite_getting-wood.png?c520b",
                        "time_to_mine": "https://minecraft.wiki/images/AchievementSprite_time-to-mine.png?fc713",
                        "hot_topic": "https://minecraft.wiki/images/AchievementSprite_hot-topic.png?ecbd7",
                        "acquire_hardware": "https://minecraft.wiki/images/AchievementSprite_acquire-hardware.png?7b885",
                        "time_to_farm": "https://minecraft.wiki/images/AchievementSprite_time-to-farm.png?cf9c0",
                        "bake_bread": "https://minecraft.wiki/images/AchievementSprite_bake-bread.png?559d6",
                        "the_lie": "https://minecraft.wiki/images/AchievementSprite_the-lie.png?5b8d6",
                        "getting_an_upgrade": "https://minecraft.wiki/images/AchievementSprite_getting-an-upgrade.png?95039",
                        "delicious_fish": "https://minecraft.wiki/images/AchievementSprite_delicious-fish.png?06b09"
                    }
                    thumbnail_url = thumbnails.get(conquista_id, "")

                    embed = discord.Embed(
                        title="🏆 Conquista Desbloqueada!",
                        description=f"Parabéns! Você completou a conquista **{conquista['nome']}**\n\n💎 **Recompensa:** 50 XP",
                        color=discord.Color.gold()
                    )
                    embed.add_field(name=conquista['emoji'] + " " + conquista['nome'], value=conquista['descricao'], inline=False)
                    if thumbnail_url:
                        embed.set_thumbnail(url=thumbnail_url)
                    embed.set_footer(text="Continue jogando para desbloquear mais conquistas!")

                    import asyncio
                    asyncio.create_task(user.send(embed=embed))
            except Exception as e:
                print(f"Erro ao enviar DM de conquista: {e}")

        return True
    return False

def get_progresso_conquista(user_id, conquista_id):
    """Retorna o progresso atual de uma conquista."""
    from utils.database import carregar_dados, get_inventario, get_blocos_quebrados
    dados = carregar_dados(user_id)
    conquista = CONQUISTAS.get(conquista_id)

    if not conquista:
        return 0, conquista["requisito"]

    tipo = conquista["tipo"]
    requisito = conquista["requisito"]

    if tipo == "nivel":
        atual = int(dados.get("nivel", 1))
        return min(atual, requisito), requisito

    elif tipo == "item":
        inventario = get_inventario(user_id)
        item = conquista["item"]
        atual = 0

        if item in inventario:
            stacks = inventario[item]
            if isinstance(stacks, list):
                atual = sum(int(s) for s in stacks)
            else:
                atual = int(stacks)

        return min(atual, requisito), requisito

    elif tipo == "blocos_quebrados":
        atual = get_blocos_quebrados(user_id)
        return min(atual, requisito), requisito

    elif tipo == "construcoes":
        inventario = get_inventario(user_id)
        atual = sum(1 for item in inventario.keys() if item.startswith("🏗️"))
        return min(atual, requisito), requisito

    elif tipo == "opened_inventory":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "collected_wood":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "crafted_pickaxe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "crafted_furnace":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "smelted_iron":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "crafted_hoe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "smelted_bread":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "crafted_cake":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "crafted_better_pickaxe":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    elif tipo == "cooked_fish":
        conquistas_completadas = dados.get("conquistas_completadas", [])
        atual = 1 if conquista_id in conquistas_completadas else 0
        return atual, requisito

    return 0, requisito