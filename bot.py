import discord
import math
import asyncio
from mcstatus import JavaServer
from discord.ext import tasks
from config import DISCORD_TOKEN, MINECRAFT_SERVER_IP, MINECRAFT_PORT, CHANNEL_ID

class MinecraftStatusBot(discord.Client):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **kwargs)
        self.server = JavaServer.lookup(f"{MINECRAFT_SERVER_IP}:{MINECRAFT_PORT}")
        self.status_message = None
        
    def server_status(self):
        try:
            status = self.server.status()
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
            print(f"Error retrieving server status: {e}")
            return {
                'online': False,
                'error': str(e)
            }

    async def setup_hook(self):
        self.update_status_loop.start()
    
    @tasks.loop(seconds=60)
    async def update_status_loop(self):
        """Update the server status message every 60 seconds"""
        if not self.is_ready():
            return
            
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Cannot find channel with ID {CHANNEL_ID}")
            return
            
        status_data = self.server_status()
        
        # Create embed based on server status
        if status_data['online']:
            embed = discord.Embed(
                title="Minecraft Server Status",
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
            
            # Add player list if available
            if status_data['player_list']:
                players_str = "\n".join(status_data['player_list'])
                if len(players_str) > 1024:  # Discord field value limit
                    players_str = players_str[:1021] + "..."
                embed.add_field(
                    name="Online Players", 
                    value=players_str or "None", 
                    inline=False
                )
                
            embed.set_footer(text=f"Last updated: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            embed = discord.Embed(
                title="Minecraft Server Status",
                description="**Server Offline**",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Error", 
                value=status_data.get('error', 'Could not connect to the server'), 
                inline=False
            )
            embed.set_footer(text=f"Last checked: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        try:
            if self.status_message:
                try:
                    await self.status_message.edit(embed=embed)
                except discord.NotFound:
                    self.status_message = await channel.send(embed=embed)
            else:
                async for message in channel.history(limit=10):
                    if message.author == self.user:
                        try:
                            await message.delete()
                        except:
                            pass
                        break
                
                self.status_message = await channel.send(embed=embed)
        except Exception as e:
            print(f"Error updating status message: {e}")
    
    @update_status_loop.before_loop
    async def before_update_loop(self):
        """Wait until the bot is ready before starting the loop"""
        await self.wait_until_ready()
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Monitoring Minecraft server at {MINECRAFT_SERVER_IP}:{MINECRAFT_PORT}')
        print(f'Sending updates to channel ID: {CHANNEL_ID}')
        print('------')

if __name__ == '__main__':
    bot = MinecraftStatusBot()
    bot.run(DISCORD_TOKEN)