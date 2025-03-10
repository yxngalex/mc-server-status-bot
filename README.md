# Minecraft Server Status Bot

## Overview

This **Discord bot** allows you to display the **Minecraft server status** in real-time, including player count and latency. It integrates with the **`mcstatus`** library to fetch the server data and uses **`discord.py`** to interact with Discord.

## Features
- **Real-time Minecraft Server Status**: Displays the number of players online and the server's latency.
- **Discord Integration**: The bot will show the server status directly in its Discord presence (e.g., "Players: 5/50").
- **Easy Setup**: Install dependencies with `pip` and configure the bot with simple environment variables.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yxngalex/mc-server-status-bot.git
cd mc-server-status-bot
```

### 2. Install dependencies
Make sure you have Python 3.x installed. Then, run the following command to install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file
Create a **`parameters.env`** file in the root directory. This file will contain the sensitive information needed to run the bot.

**Example `parameters.env` file:**
```
DISCORD_TOKEN=your_discord_bot_token
MINECRAFT_SERVER_IP=your.server.ip
MINECRAFT_PORT=25565
CHANNEL_ID=12345
```

### 4. Set up `config.py`
In the **`config.py`** file, environment variables are loaded, and the bot is configured to use them. The bot retrieves the **Discord token**, **Minecraft server IP**, and **port** from the `.env` file.

```python
import os
from dotenv import load_dotenv

# Load environment variables from parameters.env
load_dotenv("parameters.env")

# Get values
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MINECRAFT_SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
MINECRAFT_PORT = int(os.getenv("MINECRAFT_PORT", 25565))  # Default to 25565 if missing
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
```

## Usage

Run the bot with the following command:

```bash
python bot.py
```

Once the bot is running, it will automatically update its status with the **Minecraft server** details (i.e., players online and latency) and will appear in the Discord server.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Enjoy!
Feel free to fork this repository and customize the bot to suit your needs!
