# Discord Music Bot

A Python Discord bot that plays music from YouTube and Spotify in voice channels.

## Features

- Play music from YouTube by search query
- Spotify integration (tracks, playlists, and albums)
- Queue management with shuffle and clear
- Playback controls: pause, resume, skip, stop
- Auto-disconnect after 60 seconds alone in a channel

## Commands

| Command | Description |
|---------|-------------|
| !play song/url | Play from YouTube or a Spotify link |
| !pause | Pause the current song |
| !resume | Resume playback |
| !skip | Skip to the next song |
| !shuffle | Shuffle the queue |
| !clear | Clear the queue |
| !queue | Show the current queue |
| !stop | Stop playing and clear queue |
| !leave | Disconnect from voice channel |
| !help | Show all commands |

## Supported Links

- YouTube searches (e.g. !play lofi hip hop)
- Spotify tracks, playlists, and albums

## Setup

Prerequisites: Python 3.8+, FFmpeg, a Discord bot token, and Spotify API credentials.

1. Install dependencies:

    pip install -r requirements.txt

2. Create a .env file:

    DISCORD_TOKEN=your_discord_bot_token
    SPOTIFY_CLIENT_ID=your_spotify_client_id
    SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

3. Run:

    python music_bot.py

## How It Works

Spotify links are resolved to artist and track names, which are then searched on YouTube. Audio streams directly with no local downloads.
