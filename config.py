import os
from dotenv import load_dotenv

load_dotenv("parameters.env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MINECRAFT_SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
MINECRAFT_PORT = int(os.getenv("MINECRAFT_PORT"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

CHAT_CHANNEL_ID = int(os.getenv("CHAT_CHANNEL_ID"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
RCON_PORT = int(os.getenv("RCON_PORT"))
SERVER_LOG_PATH_FILE = os.getenv("SERVER_LOG_PATH_FILE")