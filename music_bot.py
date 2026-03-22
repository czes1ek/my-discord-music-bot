import discord
from discord.ext import commands
import yt_dlp
import asyncio
import traceback
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
except Exception:
    sp = None

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
        patterns = [
            r'https://open\.spotify\.com/track/',
            r'https://open\.spotify\.com/playlist/',
            r'https://open\.spotify\.com/album/'
        ]
        return any(re.match(p, url) for p in patterns)

    async def get_spotify_tracks(self, url):
        if sp is None:
            return None
        try:
            if 'track' in url:
                track = sp.track(url)
                return [track['artists'][0]['name'] + ' ' + track['name']]
            elif 'playlist' in url:
                playlist = sp.playlist(url)
                tracks = []
                for item in playlist['tracks']['items']:
                    t = item['track']
                    if t and t.get('name') and t.get('artists'):
                        tracks.append(t['artists'][0]['name'] + ' ' + t['name'])
                return tracks or None
            elif 'album' in url:
                album = sp.album(url)
                tracks = []
                for t in album['tracks']['items']:
                    if t.get('name') and t.get('artists'):
                        tracks.append(t['artists'][0]['name'] + ' ' + t['name'])
                return tracks or None
        except Exception:
            traceback.print_exc()
            return None

    @commands.command(name='play', help='Plays a song from YouTube or Spotify')
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            await ctx.send('You need to be in a voice channel to play music!')
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
                    if sp is None:
                        await ctx.send('Spotify API is not configured. Check your credentials in .env.')
                        return

                    await ctx.send('Fetching from Spotify...')
                    spotify_tracks = await self.get_spotify_tracks(search)

                    if not spotify_tracks:
                        await ctx.send('Couldn\'t fetch from Spotify!')
                        return

                    if len(spotify_tracks) > 1:
                        await ctx.send(f'Adding **{len(spotify_tracks)}** songs from Spotify to queue...')

                    added_count = 0
                    for track in spotify_tracks:
                        if await self.add_to_queue(ctx, track, voice_client, silent=True):
                            added_count += 1
                    failed_count = len(spotify_tracks) - added_count

                    if len(spotify_tracks) > 1:
                        msg = f'Added **{added_count}** songs to queue!'
                        if failed_count > 0:
                            msg += f' ({failed_count} couldn\'t be found)'
                        await ctx.send(msg)
                else:
                    await self.add_to_queue(ctx, search, voice_client)

            except Exception as e:
                await ctx.send(f'An error occurred: {str(e)}')
                traceback.print_exc()

    async def add_to_queue(self, ctx, search, voice_client, silent=False):
        try:
            loop = asyncio.get_running_loop()
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(f'ytsearch:{search}', download=False)
                )

                entries = info.get('entries') if info else None
                entry = entries[0] if entries else None

                if not entry:
                    if not silent:
                        await ctx.send(f'Couldn\'t find: **{search}**')
                    return False

                url = entry.get('url')
                title = entry.get('title', 'Unknown Title')

                if not url:
                    if not silent:
                        await ctx.send(f'Couldn\'t get stream URL for: **{search}**')
                    return False

                if ctx.guild.id not in queues:
                    queues[ctx.guild.id] = []

                queues[ctx.guild.id].append({'url': url, 'title': title, 'channel': ctx.channel})

                if not voice_client.is_playing():
                    await self.play_next(ctx.guild.id, voice_client, ctx.channel)
                elif not silent:
                    await ctx.send(f'Added to queue: **{title}**')

                return True

        except Exception:
            traceback.print_exc()
            if not silent:
                await ctx.send(f'Error adding song: {search}')
            return False

    async def play_next(self, guild_id, voice_client, channel):
        if not voice_client or not voice_client.is_connected():
            return

        if guild_id in queues and queues[guild_id]:
            try:
                song = queues[guild_id].pop(0)
                player = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
                title = song['title']

                def after_playing(error):
                    if voice_client.is_connected():
                        asyncio.run_coroutine_threadsafe(
                            self.play_next(guild_id, voice_client, channel),
                            self.bot.loop
                        )

                voice_client.play(player, after=after_playing)
                await channel.send(f'Now playing: **{title}**')
            except Exception:
                traceback.print_exc()
                await self.play_next(guild_id, voice_client, channel)

    @commands.command(name='shuffle', help='Shuffles the current queue')
    async def shuffle_queue(self, ctx):
        if ctx.guild.id not in queues or not queues[ctx.guild.id]:
            await ctx.send('Queue is empty! Nothing to shuffle.')
            return
        random.shuffle(queues[ctx.guild.id])
        await ctx.send(f'Shuffled **{len(queues[ctx.guild.id])}** songs in the queue!')

    @commands.command(name='clear', help='Clears the entire queue')
    async def clear_queue(self, ctx):
        if ctx.guild.id not in queues or not queues[ctx.guild.id]:
            await ctx.send('Queue is already empty!')
            return
        count = len(queues[ctx.guild.id])
        queues[ctx.guild.id].clear()
        await ctx.send(f'Cleared **{count}** songs from the queue!')

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Skipped!')

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('Paused!')

    @commands.command(name='resume', help='Resumes the paused song')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('Resumed!')

    @commands.command(name='stop', help='Stops playing and clears the queue')
    async def stop(self, ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.send('Stopped and cleared queue!')

    @commands.command(name='leave', help='Makes the bot leave the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client:
            if ctx.guild.id in queues:
                queues[ctx.guild.id].clear()
            await ctx.voice_client.disconnect()
            await ctx.send('Left the voice channel!')

    @commands.command(name='queue', help='Shows the current queue')
    async def show_queue(self, ctx):
        if ctx.guild.id not in queues or not queues[ctx.guild.id]:
            await ctx.send('Queue is empty!')
            return

        songs = queues[ctx.guild.id][:10]
        lines = [str(i + 1) + '. ' + s['title'] for i, s in enumerate(songs)]
        queue_list = '\n'.join(lines)

        total = len(queues[ctx.guild.id])
        if total > 10:
            queue_list += f'\n... and {total - 10} more songs'

        await ctx.send(f'**Current Queue ({total} songs):**\n{queue_list}')

    @commands.command(name='help', help='Shows all available commands')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title='Music Bot Commands',
            description='Here are all the commands you can use:',
            color=discord.Color.blue()
        )
        embed.add_field(name='!play <song/url>', value='Play from YouTube or Spotify', inline=False)
        embed.add_field(name='!pause', value='Pause the current song', inline=False)
        embed.add_field(name='!resume', value='Resume playback', inline=False)
        embed.add_field(name='!skip', value='Skip to the next song', inline=False)
        embed.add_field(name='!shuffle', value='Shuffle the current queue', inline=False)
        embed.add_field(name='!clear', value='Clear the entire queue', inline=False)
        embed.add_field(name='!queue', value='Show the current queue', inline=False)
        embed.add_field(name='!stop', value='Stop playing and clear queue', inline=False)
        embed.add_field(name='!leave', value='Disconnect from voice channel', inline=False)
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name='!help for commands'
    ))


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


async def main():
    async with bot:
        await bot.add_cog(MusicBot(bot))
        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
