import discord
from discord.ext import commands
import yt_dlp
import asyncio
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'extract_flat': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
    }],
}

FFMPEG_OPTIONS = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

queues = {}

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_spotify_url(self, url):
        spotify_patterns = [
            r'https://open\.spotify\.com/track/',
            r'https://open\.spotify\.com/playlist/',
            r'https://open\.spotify\.com/album/'
        ]
        return any(re.match(pattern, url) for pattern in spotify_patterns)

    async def get_spotify_track(self, url):
        try:
            if 'track' in url:
                track = sp.track(url)
                return [f"{track['artists'][0]['name']} {track['name']}"]
            elif 'playlist' in url:
                playlist = sp.playlist(url)
                tracks = []
                for item in playlist['tracks']['items']:
                    track = item['track']
                    if track:
                        tracks.append(f"{track['artists'][0]['name']} {track['name']}")
                return tracks
            elif 'album' in url:
                album = sp.album(url)
                tracks = []
                for track in album['tracks']['items']:
                    tracks.append(f"{track['artists'][0]['name']} {track['name']}")
                return tracks
        except Exception as e:
            print(f"Spotify error: {e}")
            return None

    @commands.command(name='play', help='Plays a song from YouTube or Spotify')
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music!")
            return

        channel = ctx.author.voice.channel
        
        if not ctx.voice_client:
            await channel.connect()
        elif ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
        
        voice_client = ctx.voice_client

        async with ctx.typing():
            try:
                if self.is_spotify_url(search):
                    await ctx.send("🎵 Fetching from Spotify...")
                    spotify_tracks = await self.get_spotify_track(search)
                    
                    if not spotify_tracks:
                        await ctx.send("Couldn't fetch from Spotify!")
                        return
                    
                    if len(spotify_tracks) > 1:
                        await ctx.send(f"Adding **{len(spotify_tracks)}** songs from Spotify to queue...")
                    
                    for track_search in spotify_tracks:
                        await self.add_to_queue(ctx, track_search, voice_client)
                    
                    if len(spotify_tracks) > 1:
                        await ctx.send(f"✅ Added **{len(spotify_tracks)}** songs to queue!")
                else:
                    await self.add_to_queue(ctx, search, voice_client)
                        
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
                print(f"Error in play command: {e}")

    async def add_to_queue(self, ctx, search, voice_client):
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{search}", download=False))
            if 'entries' in info:
                info = info['entries'][0]
            
            url = info['url']
            title = info['title']
            
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            
            queues[ctx.guild.id].append({'url': url, 'title': title, 'ctx': ctx})
            
            if not voice_client.is_playing():
                await self.play_next(ctx)
            else:
                if not self.is_spotify_url(search):
                    await ctx.send(f'Added to queue: **{title}**')

    async def play_next(self, ctx):
        if ctx.guild.id in queues and len(queues[ctx.guild.id]) > 0:
            try:
                song = queues[ctx.guild.id].pop(0)
                
                player = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
                
                def after_playing(error):
                    if error:
                        print(f"Player error: {error}")
                    asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
                
                ctx.voice_client.play(player, after=after_playing)
                
                await ctx.send(f'Now playing: **{song["title"]}**')
            except Exception as e:
                print(f"Error in play_next: {e}")
                await ctx.send(f"Error playing song: {str(e)}")
                await self.play_next(ctx)

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped!")

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused!")

    @commands.command(name='resume', help='Resumes the paused song')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed!")

    @commands.command(name='stop', help='Stops playing and clears the queue')
    async def stop(self, ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
        
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.send("Stopped and cleared queue!")

    @commands.command(name='leave', help='Makes the bot leave the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client:
            if ctx.guild.id in queues:
                queues[ctx.guild.id].clear()
            await ctx.voice_client.disconnect()
            await ctx.send("Left the voice channel!")

    @commands.command(name='queue', help='Shows the current queue')
    async def show_queue(self, ctx):
        if ctx.guild.id not in queues or len(queues[ctx.guild.id]) == 0:
            await ctx.send("Queue is empty!")
            return
        
        queue_list = "\n".join([f"{i+1}. {song['title']}" 
                               for i, song in enumerate(queues[ctx.guild.id])])
        await ctx.send(f"**Current Queue:**\n{queue_list}")

    @commands.command(name='help', help='Shows all available commands')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🎵 Music Bot Commands",
            description="Here are all the commands you can use:",
            color=discord.Color.blue()
        )
        embed.add_field(name="!play <song/url>", value="Play from YouTube or Spotify", inline=False)
        embed.add_field(name="!pause", value="Pause the current song", inline=False)
        embed.add_field(name="!resume", value="Resume playback", inline=False)
        embed.add_field(name="!skip", value="Skip to the next song", inline=False)
        embed.add_field(name="!queue", value="Show the current queue", inline=False)
        embed.add_field(name="!stop", value="Stop playing and clear queue", inline=False)
        embed.add_field(name="!leave", value="Disconnect from voice channel", inline=False)
        embed.set_footer(text="Now supports Spotify links! 🎵")
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="!help for commands"
    ))
    await bot.add_cog(MusicBot(bot))

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = member.guild.voice_client
    if voice_client and voice_client.channel:
        if len(voice_client.channel.members) == 1:
            await asyncio.sleep(60)
            if voice_client and len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                if member.guild.id in queues:
                    queues[member.guild.id].clear()

bot.run(TOKEN)