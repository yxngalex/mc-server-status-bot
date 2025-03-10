import os
from dotenv import load_dotenv

load_dotenv("parameters.env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MINECRAFT_SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
MINECRAFT_PORT = int(os.getenv("MINECRAFT_PORT"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))