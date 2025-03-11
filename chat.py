import asyncio
import re
from mcstatus import JavaServer
from mcrcon import MCRcon
from config import (
    MINECRAFT_SERVER_IP,
    RCON_PASSWORD, 
    RCON_PORT,
    CHAT_CHANNEL_ID,
    SERVER_LOG_PATH_FILE
)

class ChatIntegration:
    def __init__(self, bot):
        self.bot = bot
        self.chat_channel = None
        self.last_log_position = 0
        self.log_file_path = str(SERVER_LOG_PATH_FILE)
        
    async def initialize(self):
        self.chat_channel = self.bot.get_channel(CHAT_CHANNEL_ID)
        if not self.chat_channel:
            print(f"Cannot find chat channel with ID {CHAT_CHANNEL_ID}")
            return False
        
        self.bot.loop.create_task(self.monitor_server_logs())
        return True
        
    async def monitor_server_logs(self):
        while True:
            try:
                server = JavaServer.lookup(f"{MINECRAFT_SERVER_IP}")
                try:
                    status = server.status()
                    with open(self.log_file_path, 'r', encoding='utf-8') as log_file:
                        log_file.seek(max(0, self.last_log_position))
                        
                        new_lines = log_file.readlines()
                        
                        self.last_log_position = log_file.tell()
                        
                        for line in new_lines:
                            await self.process_log_line(line)
                except:
                    print("Vanilla server appears to be offline. Chat integration paused.")
                    await asyncio.sleep(30)
                    continue
                        
            except FileNotFoundError:
                print(f"Warning: Log file not found at {self.log_file_path}")
            except Exception as e:
                print(f"Error monitoring server logs: {e}")
                
            await asyncio.sleep(2)
    
    async def process_log_line(self, line):
        chat_match = re.search(r'\[\d+:\d+:\d+\] \[Server thread/INFO\]: <([^>]+)> (.*)', line)
        if chat_match:
            player_name = chat_match.group(1)
            message = chat_match.group(2)
            await self.send_to_discord(player_name, message)
            return
            
        death_match = re.search(r'\[\d+:\d+:\d+\] \[Server thread/INFO\]: (.*) (died|was slain|fell|drowned|burned|was shot)', line)
        if death_match:
            event = death_match.group(0).split('INFO]: ')[1]
            await self.send_event_to_discord(event)
            return
    
    async def send_to_discord(self, player_name, message):
        if self.chat_channel:
            try:
                await self.chat_channel.send(f"**{player_name}**: {message}")
            except Exception as e:
                print(f"Error sending message to Discord: {e}")
    
    async def send_event_to_discord(self, event):
        if self.chat_channel:
            try:
                await self.chat_channel.send(f"*{event}*")
            except Exception as e:
                print(f"Error sending event to Discord: {e}")
    
    async def send_to_minecraft(self, author, message):
        try:
            with MCRcon(MINECRAFT_SERVER_IP, RCON_PASSWORD, port=RCON_PORT) as mcr:
                formatted_message = f"tellraw @a {{\"text\":\"\",\"extra\":[{{\"text\":\"[Discord] \",\"color\":\"blue\"}},{{\"text\":\"{author}: \",\"color\":\"white\"}},{{\"text\":\"{message}\",\"color\":\"gray\"}}]}}"
                mcr.command(formatted_message)
        except Exception as e:
            print(f"Error sending message to Minecraft: {e}")

def setup(bot):
    chat_integration = ChatIntegration(bot)
    
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        if message.channel.id == CHAT_CHANNEL_ID:
            await chat_integration.send_to_minecraft(message.author.display_name, message.content)
        
        # await bot.process_commands(message)
    
    return chat_integration