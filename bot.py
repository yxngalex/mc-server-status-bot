import discord
import math
import asyncio
from mcstatus import JavaServer
from discord.ext import tasks
from config import DISCORD_TOKEN, CHANNEL_ID, MINECRAFT_SERVER_IP, MINECRAFT_PORT
import chat

class MinecraftStatusBot(discord.Client):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **kwargs)
        
        self.servers = [
            {
                "server": JavaServer.lookup(f"{MINECRAFT_SERVER_IP}:{MINECRAFT_PORT}"),
                "name": "MODDED", 
                "status_message": None,
                "icon_path": "images/modded.jpg"
            },
            {
                "server": JavaServer.lookup(f"{MINECRAFT_SERVER_IP}"),
                "name": "VANILLA",
                "status_message": None,
                "icon_path": "images/vanilla.jpg"
            }
        ]
        
    def get_server_status(self, server):
        try:
            status = server.status()
            latency = math.floor(status.latency)
            online_players = status.players.online
            max_players = status.players.max
            motd = status.description.to_plain_text() if hasattr(status.description, 'to_plain_text') else str(status.description)
            
            player_list = []
            if hasattr(status.players, 'sample') and status.players.sample:
                player_list = [player.name for player in status.players.sample]
                
            return {
                'online': True,
                'players': online_players,
                'max_players': max_players,
                'latency': latency,
                'motd': motd,
                'player_list': player_list
            }
        except Exception as e:
            return {
                'online': False,
                'error': str(e)
            }

    async def setup_hook(self):
        self.update_status_loop.start()

        self.chat_integration = chat.setup(self)
        await self.chat_integration.initialize()
    
    @tasks.loop(seconds=60)
    async def update_status_loop(self):
        if not self.is_ready():
            return
            
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Cannot find channel with ID {CHANNEL_ID}")
            return
        
        for server_info in self.servers:
            status_data = self.get_server_status(server_info["server"])
            
            filename = server_info["icon_path"].split("/")[-1]
            icon_file = discord.File(server_info["icon_path"], filename=filename)
            
            if status_data['online']:
                embed = discord.Embed(
                    title=f"{server_info['name']} Status",
                    description=status_data['motd'],
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Players", 
                    value=f"{status_data['players']}/{status_data['max_players']}", 
                    inline=True
                )
                embed.add_field(
                    name="Latency", 
                    value=f"{status_data['latency']} ms", 
                    inline=True
                )
                
                if status_data['player_list']:
                    players_str = "\n".join(status_data['player_list'])
                    if len(players_str) > 1024:
                        players_str = players_str[:1021] + "..."
                    embed.add_field(
                        name="Online Players", 
                        value=players_str or "None", 
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title=f"{server_info['name']} Status",
                    description="**Server Offline**",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Error", 
                    value=status_data.get('error', 'Could not connect to the server'), 
                    inline=False
                )
            
            embed.set_author(
                name=server_info['name'],
                icon_url=f"attachment://{filename}"
            )
            
            embed.set_footer(text=f"Last updated: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            try:
                if server_info["status_message"]:
                    try:
                        new_icon_file = discord.File(server_info["icon_path"], filename=filename)
                        await server_info["status_message"].edit(embed=embed, attachments=[new_icon_file])
                    except discord.NotFound:
                        server_info["status_message"] = await channel.send(file=icon_file, embed=embed)
                else:
                    found_message = False
                    async for message in channel.history(limit=20):
                        if message.author == self.user and message.embeds and message.embeds[0].title.startswith(server_info["name"]):
                            try:
                                new_icon_file = discord.File(server_info["icon_path"], filename=filename)
                                await message.edit(embed=embed, attachments=[new_icon_file])
                                server_info["status_message"] = message
                                found_message = True
                                break
                            except Exception as edit_error:
                                print(f"Error editing message: {edit_error}")
                    
                    if not found_message:
                        server_info["status_message"] = await channel.send(file=icon_file, embed=embed)
            except Exception as e:
                print(f"Error updating status message for {server_info['name']}: {e}")
    
    @update_status_loop.before_loop
    async def before_update_loop(self):
        await self.wait_until_ready()
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('Monitoring Minecraft servers:')
        for idx, server_info in enumerate(self.servers):
            server_address = f"{MINECRAFT_SERVER_IP}:{MINECRAFT_PORT}" if idx == 0 else f"{MINECRAFT_SERVER_IP}"
            print(f'- {server_info["name"]}: {server_address} (Icon: {server_info["icon_path"]})')
        print(f'Sending updates to channel ID: {CHANNEL_ID}')
        print('------')

if __name__ == '__main__':
    bot = MinecraftStatusBot()
    bot.run(DISCORD_TOKEN)