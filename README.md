# Discord Music Bot

A feature-rich Python Discord bot that plays music from YouTube and Spotify in voice channels with advanced queue management and playback controls.

## Features

- 🎵 Play music from YouTube by search query
- 🎧 Full Spotify integration (tracks, playlists, and albums)
- 📝 Advanced queue management system
- 🔀 Shuffle functionality for randomizing playlists
- 🗑️ Clear queue command
- ⏯️ Complete playback controls (pause, resume, skip, stop)
- 📋 Display current queue with song count
- 🤖 Auto-disconnect when inactive (60 seconds alone in channel)
- 💬 Beautiful embed help menu
- 🔄 Automatic reconnection and comprehensive error handling
- 🛡️ Graceful shutdown to prevent error spam

## Commands

| Command | Description |
|---------|-------------|
| `!play <song/url>` | Play a song from YouTube or Spotify link |
| `!pause` | Pause the current song |
| `!resume` | Resume playback |
| `!skip` | Skip to the next song |
| `!shuffle` | Shuffle the current queue |
| `!clear` | Clear the entire queue (keeps current song playing) |
| `!queue` | Show the current queue (displays first 10 songs) |
| `!stop` | Stop playing and clear queue |
| `!leave` | Disconnect from voice channel |
| `!help` | Show all commands with descriptions |

## Supported Links

- **YouTube searches** (e.g., `!play lofi hip hop beats`)
- **Spotify tracks**: `https://open.spotify.com/track/...`
- **Spotify playlists**: `https://open.spotify.com/playlist/...`
- **Spotify albums**: `https://open.spotify.com/album/...`

## How It Works

1. When you provide a Spotify link, the bot fetches track information using the Spotify API
2. It then searches YouTube for each song using the artist name and track title
3. Audio is streamed directly from YouTube (no downloads required)
4. Songs are queued and played sequentially in the voice channel
5. Failed tracks are automatically skipped with error reporting

## Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Discord Bot Token
- Spotify API Credentials (Client ID and Secret)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/discord-music-bot.git
cd discord-music-bot
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg:**
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH, or use `choco install ffmpeg`
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

4. **Set up Discord Bot:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section and click "Add Bot"
   - Enable these Privileged Gateway Intents:
     - Presence Intent
     - Server Members Intent
     - Message Content Intent
   - Click "Reset Token" and copy your bot token

5. **Set up Spotify API:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create an App"
   - Copy your Client ID and Client Secret

6. **Create a `.env` file** in the project directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
```

7. **Invite the bot to your server:**
   - In Discord Developer Portal, go to OAuth2 → URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select bot permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`
   - Copy the generated URL and open it to invite your bot

### Running the Bot
```bash
python music_bot.py
```

The bot should now be online in your Discord server!

To stop the bot, press `Ctrl + C` in the terminal. The bot will gracefully disconnect from all voice channels and shut down cleanly.

## Usage Examples

### Play a song from YouTube:
```
!play never gonna give you up
```

### Play a Spotify track:
```
!play https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
```

### Play a Spotify playlist:
```
!play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Shuffle the queue:
```
!shuffle
```

### View the queue:
```
!queue
```

### Clear all queued songs:
```
!clear
```

## Project Structure
```
discord-music-bot/
├── music_bot.py          # Main bot code
├── .env                  # Environment variables (tokens)
├── .env.example          # Template for environment variables
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
├── README.md            # This file
└── LICENSE              # MIT License
```

## Technologies Used

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper for Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader and audio extractor
- [spotipy](https://github.com/plamere/spotipy) - Spotify Web API wrapper
- [FFmpeg](https://ffmpeg.org/) - Audio and video processing
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

## Hosting

This bot can be hosted 24/7 on various platforms for continuous uptime:

### Recommended Options:

- **PebbleHost** ($1-2/month) - Dedicated bot hosting, easy setup
- **Oracle Cloud** (Free forever) - Free tier with generous resources
- **Heroku** (Free tier available) - Easy deployment with Git
- **Replit** (Free tier available) - Quick testing and development

### Resource Requirements:

- **Storage:** ~200-300 MB
- **RAM:** 512 MB - 1 GB recommended
- **Bandwidth:** Moderate (for audio streaming)

The bot is lightweight and does not download songs locally - all audio is streamed directly.

## Troubleshooting

### Bot doesn't play audio:
- Ensure FFmpeg is properly installed and in your system PATH
- Check that the bot has "Connect" and "Speak" permissions in your Discord server
- Verify you're in a voice channel before using `!play`

### "ffmpeg was not found" error:
- Install FFmpeg using the instructions above
- Restart your terminal/PowerShell after installation
- Verify installation with `ffmpeg -version`

### Spotify links not working:
- Verify your Spotify API credentials in the `.env` file
- Check that the Spotify link is public and accessible
- Look for error messages in the console for more details

### Bot disconnects randomly:
- This is normal behavior when the queue is empty
- The bot auto-disconnects after 60 seconds if alone in a voice channel
- Use `!stop` or `!leave` to manually disconnect

### "list index out of range" error:
- This usually means a song couldn't be found on YouTube
- The bot will skip failed songs and report how many couldn't be added
- Check your internet connection

### Error messages when stopping the bot:
- Use `Ctrl + C` to stop - the bot now shuts down gracefully
- All voice connections are properly closed before shutdown

## Contributing

Contributions are welcome! Feel free to:
- Report bugs by opening an issue
- Suggest new features
- Submit pull requests with improvements

## Security Notes

- Never share your `.env` file or commit it to GitHub
- Always use the `.gitignore` file to protect sensitive data
- Regenerate tokens immediately if accidentally exposed
- Use environment variables when deploying to hosting platforms

## Future Feature Ideas

- Volume control
- Loop/repeat functionality
- Save custom playlists
- Play from SoundCloud
- Lyrics display
- Now playing with progress bar
- Voting system for skipping songs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes. Ensure you comply with:
- YouTube's Terms of Service
- Spotify's Terms of Use
- Discord's Terms of Service and Community Guidelines

## Acknowledgments

- Thanks to the discord.py community for excellent documentation
- yt-dlp developers for maintaining a robust YouTube downloader
- Spotify for their comprehensive Web API

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review console output for detailed error messages
3. Ensure all dependencies are properly installed
4. Verify your `.env` file has correct credentials

---

**Made with ❤️ for music lovers**

*Enjoy your music bot!* 🎵