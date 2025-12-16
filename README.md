# my-discord-music-bot
This was a short project I created using Python. I made a Discord bot for my personal discord server.

## Commands
- `!play <song>` - Play a song from YouTube
- `!pause` - Pause the current song
- `!resume` - Resume playback
- `!skip` - Skip to the next song
- `!queue` - Show the current queue
- `!stop` - Stop playing and clear queue
- `!leave` - Disconnect from voice channel
- `!help` - Show all commands

## Setup

### Prerequisites
- Python 3.8+
- FFmpeg installed on your system

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/discord-music-bot.git
cd discord-music-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

4. Get your Discord bot token:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the token and paste it in your `.env` file

5. Install FFmpeg:
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

### Running the Bot
```bash
python music_bot.py
```

## Usage

1. Invite the bot to your Discord server
2. Join a voice channel
3. Use `!play <song name>` to start playing music
4. Use `!help` to see all available commands
