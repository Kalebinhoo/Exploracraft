import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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
    print("🔐 Usando configurações do arquivo .env")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def carregar_cogs():
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

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"🆔 ID do Bot: {bot.user.id}")
    print(f"🔧 Prefixo: {PREFIX}")

    await bot.change_presence(
        activity=discord.Game(name="Sobrevivência"),
        status=discord.Status.online
    )

    await carregar_cogs()
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

print("🚀 Tentando iniciar o bot...")
print(f"🔐 Token configurado: {'✅' if TOKEN else '❌'}")
print(f"🔧 Prefixo configurado: {PREFIX}")

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ Erro ao iniciar o bot: {e}")
    if "Improper token" in str(e):
        print("💡 Dica: Verifique se o token no arquivo .env está correto!")
    elif "Privileged message content intent" in str(e):
        print("💡 Dica: Ative as 'Privileged Gateway Intents' no Discord Developer Portal!")