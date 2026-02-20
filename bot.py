import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import asyncio
from utils.database import init_db

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if not os.path.exists("cogs"):
    parent_dir = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(parent_dir, "cogs")):
        os.chdir(parent_dir)
    else:
        print("❌ Error: cogs directory not found. Please run the bot from the correct directory.")
        exit()

import sys
sys.path.insert(0, os.getcwd())

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")
CLIENT_ID = os.getenv("CLIENT_ID")

if not TOKEN:
    print("❌ Token não encontrado! Verifique o arquivo .env")
    exit()
else:
    print("Usando configuracoes do arquivo .env")

intents = discord.Intents.all()

async def carregar_cogs(bot):
    if os.path.exists("cogs"):
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ Cog carregado: {filename}")
                except Exception as e:
                    print(f"❌ Erro ao carregar cog {filename}: {e}")
    else:
        print("⚠️ Pasta 'cogs/' não encontrada.")

async def setup_bot():
    bot = commands.Bot(command_prefix=PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        init_db()
        print("Database initialized.")

        print(f"Bot conectado como {bot.user}")
        print(f"ID do Bot: {bot.user.id}")
        print(f"Prefixo: {PREFIX}")
        try:
            with open('inventarios.json', 'r', encoding='utf-8') as f:
                inventarios = json.load(f)
            registered_users = {user_id for user_id, data in inventarios.items() if isinstance(data, dict) and data.get('registrado')}
            registered_count = len(registered_users)
            print(f"Numero de membros registrados: {registered_count}")
        except FileNotFoundError:
            print("Arquivo inventarios.json nao encontrado.")
            registered_users = set()
            registered_count = 0
        except json.JSONDecodeError:
            print("Erro ao ler inventarios.json.")
            registered_users = set()
            registered_count = 0
        except Exception as e:
            print(f"Erro ao contar membros registrados: {e}")
            registered_users = set()
            registered_count = 0

        async def cycle_status():
            guild_count = len(bot.guilds)
            statuses = [
                discord.Game(name=f"🌐 Em {guild_count} servidores!"),
                discord.Game(name="🌐 https://discord.gg/RTwZ4zzQ"),
                discord.Game(name="🟢 Xp infinito"),
                discord.Game(name="🌎 ExploraCraft"),
                discord.Game(name="🧟⚔ Matando zumbis"),
                discord.Game(name="💰 Lucros de Minecoins")
            ]
            index = 0
            while True:
                await bot.change_presence(activity=statuses[index], status=discord.Status.online)
                index = (index + 1) % len(statuses)
                await asyncio.sleep(30)

        bot.loop.create_task(cycle_status())

        async def hunger_task():
            while True:
                try:
                    from utils.database import inventarios, salvar_inventarios, alterar_fome
                    import time

                    current_time = int(time.time())
                    for user_id, data in inventarios.items():
                        if isinstance(data, dict):
                            last_update = data.get("last_update", current_time)
                            if current_time - last_update >= 1800:
                                hunger = data.get("fome", 10)
                                if hunger > 0:
                                    data["fome"] = max(0, hunger - 1)
                                    data["last_update"] = current_time
                                    if data["fome"] == 0:
                                        vida = data.get("vida", 10)
                                        data["vida"] = max(0, vida - 1)
                    salvar_inventarios()
                except Exception as e:
                    print(f"Erro na tarefa de fome: {e}")
                await asyncio.sleep(300)

        bot.loop.create_task(hunger_task())

        @bot.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
            """Handler global para erros de slash commands."""
            try:
                print(f"Erro em comando slash: {error}")
                print(f"Comando: {interaction.command.name if interaction.command else 'N/A'}")
                print(f"Usuário: {interaction.user}")
                print(f"Guild: {interaction.guild}")
                
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ **Ocorreu um erro inesperado!**\n\n"
                        "Por favor, tente novamente em alguns segundos. "
                        "Se o problema persistir, contate o suporte.",
                        ephemeral=True
                    )
            except Exception as e:
                print(f"Erro no handler de erro: {e}")

        print("\n--- Servidores do Bot ---")
        total_registered_sum = 0
        for guild in bot.guilds:
            registered_in_guild = sum(1 for member in guild.members if str(member.id) in registered_users)
            print(f"Servidor: {guild.name} - Usuários registrados: {registered_in_guild}")
            total_registered_sum += registered_in_guild
        print(f"Soma total de usuários registrados em todos os servidores: {total_registered_sum}")

        await carregar_cogs(bot)
        try:
            GUILD_ID = os.getenv("GUILD_ID")
            if GUILD_ID:
                await bot.tree.sync(guild=discord.Object(id=int(GUILD_ID)))
                print(f"🔁 Comandos sincronizados com sucesso no servidor: {GUILD_ID}")
            else:
                synced = await bot.tree.sync()
                print(f"🌍 {len(synced)} comandos sincronizados globalmente")
        except Exception as e:
            print(f"❌ Erro ao sincronizar comandos: {e}")

    return bot

async def main():
    print("Tentando iniciar o bot...")
    print(f"Token configurado: {'SIM' if TOKEN else 'NAO'}")
    print(f"Prefixo configurado: {PREFIX}")
    
    try:
        bot = await setup_bot()
        await bot.start(TOKEN)
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
        if "Improper token" in str(e):
            print("💡 Dica: Verifique se o token no arquivo .env está correto!")
        elif "Privileged message content intent" in str(e):
            print("💡 Dica: Ative as 'Privileged Gateway Intents' no Discord Developer Portal!")

if __name__ == "__main__":
    asyncio.run(main())
