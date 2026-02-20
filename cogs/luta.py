import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from utils.database import get_inventario, is_command_under_maintenance
from icons.emojis import EMOJIS

ATTACK_MESSAGES = [
    "{attacker} atacou com {weapon} e causou {damage} de dano!",
    "{attacker} desferiu um golpe poderoso com {weapon}! {damage} de dano!",
    "{attacker} brandiu {weapon} e acertou em cheio! {damage} HP perdidos!",
    "{attacker} lançou um ataque selvagem com {weapon}! -{damage} HP!",
]

DODGE_MESSAGES = [
    "{defender} tentou desviar... e conseguiu! 🎉",
    "{defender} se esquivou habilmente da investida! ✨",
    "{defender} pulou para o lado bem na hora! 😅",
    "{defender} desviou como um ninja! 🥷",
]

FAIL_DODGE_MESSAGES = [
    "{defender} tentou desviar... mas tropeçou! 😂",
    "{defender} escorregou e levou o golpe! 🤕",
    "{defender} tentou pular, mas caiu de cara! 😵",
    "{defender} dançou para desviar, mas dançou mal! 💃❌",
]

MISS_MESSAGES = [
    "{attacker} atacou com {weapon}... e errou completamente! 😅",
    "{attacker} mirou com {weapon}, mas o alvo sumiu! 🎭",
    "{attacker} balançou {weapon} no ar! 💨",
    "{attacker} tentou acertar, mas só acertou o vento! 🌪️",
]

COUNTER_MESSAGES = [
    "{defender} contra-atacou enquanto {attacker} errava! ⚡",
    "{defender} aproveitou a falha e revidou! 💥",
    "{defender} viu a abertura e contra-atacou! 🎯",
]

FUN_REACTIONS = [
    "{player} riu e se preparou para o próximo ataque! 😂",
    "{player} fez uma dancinha de vitória! 🕺",
    "{player} gritou 'É isso aí!' 🎉",
    "{player} piscou para a plateia! 😉",
    "{player} flexionou os músculos! 💪",
    "{player} fez pose de campeão! 🏆",
]

FINAL_MESSAGES = [
    "{winner} desferiu o golpe final e derrotou {loser}! 💥",
    "{winner} venceu por nocaute técnico! {loser} está caído! 😵",
    "{winner} é o campeão! {loser} se rende! 🏆",
    "{winner} ganhou a batalha! {loser} precisa treinar mais! 💪",
]

class FunBattleView(discord.ui.View):
    def __init__(self, challenger, target):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.accepted = False

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.target:
            return await interaction.response.send_message("Este desafio não é para você!", ephemeral=True)

        self.accepted = True
        await interaction.response.send_message("Desafio aceito! Preparando a batalha...", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.target:
            return await interaction.response.send_message("Este desafio não é para você!", ephemeral=True)

        await interaction.response.send_message("Desafio recusado.", ephemeral=True)
        self.stop()

class Luta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_player_weapon(self, user_id):
        """Get the best weapon a player has"""
        inventory = get_inventario(user_id)

        weapon_priority = [
            "espada de diamante", "espada de ferro", "espada de ouro", "espada de pedra", "espada de madeira",
            "machado de diamante", "machado de ferro", "machado de ouro", "machado de pedra", "machado de madeira",
            "arco"
        ]

        for weapon in weapon_priority:
            if weapon in inventory:
                qty = inventory[weapon]
                if isinstance(qty, list):
                    total = sum(qty)
                else:
                    total = qty
                if total > 0:
                    return weapon

        return "punhos"

    def get_weapon_damage(self, weapon):
        """Get damage for a weapon"""
        damage_values = {
            "espada de diamante": (7, 9),
            "espada de ferro": (6, 8),
            "espada de ouro": (4, 6),
            "espada de pedra": (5, 7),
            "espada de madeira": (4, 6),
            "machado de diamante": (6, 8),
            "machado de ferro": (5, 7),
            "machado de ouro": (3, 5),
            "machado de pedra": (4, 6),
            "machado de madeira": (3, 5),
            "arco": (3, 5),
            "punhos": (1, 3)
        }
        return damage_values.get(weapon, (1, 3))

    def get_weapon_emoji(self, weapon):
        """Get emoji for a weapon"""
        weapon_emojis = {
            "espada de diamante": "⚔️",
            "espada de ferro": "⚔️",
            "espada de ouro": "⚔️",
            "espada de pedra": "⚔️",
            "espada de madeira": "⚔️",
            "machado de diamante": "🪓",
            "machado de ferro": "🪓",
            "machado de ouro": "🪓",
            "machado de pedra": "🪓",
            "machado de madeira": "🪓",
            "arco": "🏹",
            "punhos": "👊"
        }
        return weapon_emojis.get(weapon, "👊")

    async def simulate_fun_battle(self, interaction, player1, player2):
        """Simulate a fun, narrative battle"""
        p1_weapon = self.get_player_weapon(player1.id)
        p2_weapon = self.get_player_weapon(player2.id)

        p1_health = 100
        p2_health = 100

        battle_log = []
        turn = 1
        max_turns = 15

        embed = discord.Embed(
            title="⚔️ Batalha Épica Começa!",
            description=f"**{player1.name}** vs **{player2.name}**\n\nQue comece a batalha!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

        while p1_health > 0 and p2_health > 0 and turn <= max_turns:
            battle_log.append(f"\n🔁 **Turno {turn}:**")

            current_player = player1
            opponent = player2
            current_weapon = p1_weapon
            current_health = p1_health
            opponent_health = p2_health

            action_msg = await self.simulate_turn(interaction, current_player, opponent, current_weapon, opponent_health)
            battle_log.extend(action_msg)

            damage_dealt = self.extract_damage_from_message(action_msg[-1]) if action_msg else 0
            if turn % 2 == 1:
                p2_health -= damage_dealt
            else:
                p1_health -= damage_dealt

            player1, player2 = player2, player1
            p1_weapon, p2_weapon = p2_weapon, p1_weapon
            p1_health, p2_health = p2_health, p1_health
            turn += 1

        if p1_health <= 0:
            winner = player2
            loser = player1
        elif p2_health <= 0:
            winner = player1
            loser = player2
        else:
            winner = random.choice([player1, player2])
            loser = player1 if winner == player2 else player2

        final_msg = random.choice(FINAL_MESSAGES).format(winner=winner.name, loser=loser.name)

        embed = discord.Embed(
            title="🏆 Batalha Concluída!",
            description=f"{final_msg}\n\n**Vencedor:** {winner.mention}\n**Perdedor:** {loser.mention}",
            color=discord.Color.gold()
        )

        summary = "\n".join(battle_log[-8:])
        if summary:
            embed.add_field(name="📜 Últimas Ações", value=summary, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    def extract_damage_from_message(self, message):
        """Extract damage value from battle message"""
        import re
        damage_match = re.search(r'(\d+)\s*(?:de dano|HP|dano)', message)
        if damage_match:
            return int(damage_match.group(1))
        return 0

    async def simulate_turn(self, interaction, attacker, defender, weapon, defender_health):
        """Simulate one turn of battle"""
        messages = []

        weapon_emoji = self.get_weapon_emoji(weapon)
        weapon_display = f"{weapon_emoji} {weapon.title()}" if weapon != "punhos" else "👊 Punhos"

        action_type = random.choices(
            ['attack', 'dodge_attempt', 'miss'],
            weights=[0.6, 0.3, 0.1]
        )[0]

        if action_type == 'attack':
            damage_range = self.get_weapon_damage(weapon)
            damage = random.randint(damage_range[0], damage_range[1])

            attack_msg = random.choice(ATTACK_MESSAGES).format(
                attacker=attacker.name,
                weapon=weapon_display,
                damage=damage
            )
            messages.append(attack_msg)

            if random.random() < 0.3:
                reaction = random.choice(FUN_REACTIONS).format(player=attacker.name)
                messages.append(reaction)

        elif action_type == 'dodge_attempt':
            dodge_success = random.random() < 0.5

            if dodge_success:
                dodge_msg = random.choice(DODGE_MESSAGES).format(defender=defender.name)
                messages.append(dodge_msg)

                if random.random() < 0.4:
                    counter_msg = random.choice(COUNTER_MESSAGES).format(
                        defender=defender.name,
                        attacker=attacker.name
                    )
                    messages.append(counter_msg)
            else:
                fail_dodge_msg = random.choice(FAIL_DODGE_MESSAGES).format(defender=defender.name)
                messages.append(fail_dodge_msg)

                damage_range = self.get_weapon_damage(weapon)
                damage = random.randint(damage_range[0], damage_range[1])

                attack_msg = random.choice(ATTACK_MESSAGES).format(
                    attacker=attacker.name,
                    weapon=weapon_display,
                    damage=damage
                )
                messages.append(attack_msg)

        else:
            miss_msg = random.choice(MISS_MESSAGES).format(
                attacker=attacker.name,
                weapon=weapon_display
            )
            messages.append(miss_msg)

            if random.random() < 0.4:
                reaction = random.choice(FUN_REACTIONS).format(player=defender.name)
                messages.append(reaction)

        for msg in messages:
            embed = discord.Embed(description=msg, color=discord.Color.blue())
            await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio.sleep(1.5)

        return messages

    @app_commands.command(name="luta", description="Desafie outro jogador para uma batalha divertida!")
    @app_commands.describe(jogador="Jogador que você quer desafiar para uma batalha épica (mencione ou digite o nome)")
    async def luta(self, interaction: discord.Interaction, jogador: str):
        target = None

        if jogador.startswith('<@') and jogador.endswith('>'):
            try:
                user_id = int(jogador.strip('<@!>'))
                target = interaction.guild.get_member(user_id)
            except ValueError:
                pass
        else:
            target = interaction.guild.get_member_named(jogador)

        if not target:
            return await interaction.response.send_message("Jogador não encontrado! Certifique-se de mencionar o usuário ou digitar o nome corretamente.", ephemeral=True)

        if is_command_under_maintenance("luta"):
            embed = discord.Embed(
                title="🔧 Comando em Manutenção",
                description="O comando /luta está temporariamente indisponível devido a manutenção.\n\nVolte em breve!",
                color=0x81919E
            )
            embed.set_thumbnail(url="https://minecraft.wiki/images/Clockwise_Gear_%28N%29.gif?d648f")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if target == interaction.user:
            return await interaction.response.send_message("Você não pode lutar contra si mesmo! 🤪", ephemeral=True)

        if target.bot:
            return await interaction.response.send_message("Você não pode desafiar bots! 🤖", ephemeral=True)

        embed = discord.Embed(
            title="⚔️ Desafio de Batalha!",
            description=f"{interaction.user.mention} desafiou {target.mention} para uma batalha épica!\n\nSerá que {target.name} aceita o desafio?",
            color=discord.Color.orange()
        )

        view = FunBattleView(interaction.user, target)

        try:
            await target.send(embed=embed, view=view)
            await interaction.response.send_message("Desafio enviado! Que comece a batalha! ⚔️", ephemeral=True)
        except:
            await interaction.response.send_message("Não foi possível enviar o desafio. O jogador pode ter DMs desabilitadas.", ephemeral=True)
            return

        await view.wait()

        if view.accepted:
            await self.simulate_fun_battle(interaction, interaction.user, target)
        else:
            embed = discord.Embed(
                title="😔 Desafio Recusado",
                description=f"{target.name} recusou o desafio de {interaction.user.name}.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Luta(bot))
