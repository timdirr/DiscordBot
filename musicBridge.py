import sys
import discord
from discord.ext import commands
import traceback
import asyncio

sys.path.insert(0, 'music/')
import spotifyParser
import musicPlayer

async def play(url, ctx : commands.Context, bot : discord.Client):
    tracks = spotifyParser.getSongs(url)
    x = ''
    for t in tracks:
        x += f'{t}\n'

    last5 = ''
    for i, x in enumerate(tracks[:6]):
        last5 += f'**{i}**- {x["trackName"]} [by: {x["artist"]}]\n'
     
    embed = discord.Embed(
        title=f'Queue: {len(tracks)} songs.',
        description=f'Now Playing: **{tracks[0]["trackName"]}**',
        color=0xff866f
    )
    embed.add_field(name='Author:', value=f'{tracks[0]["artist"]}', inline=True)
    embed.add_field(name='Loop:', value=f'False', inline=True)
    embed.add_field(name='Last 5 in queue', value=f'{last5}', inline=False)
    embed.set_footer(text='🍑 the best bot 🎶')
     
    try: #try connecting to vc
        vchannel = bot.get_channel(ctx.author.voice.channel.id)
    except AttributeError:
        await ctx.send('Devi essere in un culo vocale per usare questo comando.')
        await ctx.message.add_reaction('❌')
        return
    except discord.ClientException:
        await ctx.send('Sono già in un altro canale vocale.')
        await ctx.message.add_reaction('❌')
    else:
        
        voice : discord.VoiceClient = await vchannel.connect()

        await ctx.message.add_reaction('🍑')

    embedMSG = await ctx.send(embed=embed)
    #embedMSG.add_reaction('🔀🔂⏩⏪⏸▶')
    
    player = musicPlayer.Player(bot, voice, tracks, embed)

    try:
        player.playNext()
    except Exception as e:
        await voice.disconnect()
        voice.cleanup()
        ex, val, tb = sys.exc_info()
        traceback.print_exception(ex, val, tb)

    def check(m : discord.Message):	#check if message was sent in thread using ID
        return m.author != bot.user and m.channel.id == ctx.channel.id

    lastSong = player.queue[0]
    while True:
        userMessage : discord.Message = await bot.wait_for('message', check=check)	

        if userMessage.content == '!skip':
            player.skip()
            await asyncio.sleep(0.6)

        elif userMessage.content == '!pause':
            player.pause()

        elif userMessage.content == '!shuffle':
            player.shuffle()
            await userMessage.add_reaction('🔀')
            await userMessage.add_reaction('✅')
            
        elif userMessage.content == '!resume':
            player.resume()

        elif userMessage.content == '!stop':
            await player.stop()
            return 0
        
        elif userMessage.content == '!clear':
            player.clear()

        elif userMessage.content == '!loop':
            player.loop = True
            await userMessage.add_reaction('🔂')

        elif userMessage.content == '!queue':
            embedMSG = await ctx.send(embed=player.embed)

        elif userMessage.content == '!add':
            pass #TODO append new songs at start/end of queue

        if lastSong != player.queue[0] or userMessage.content in ['!shuffle', '!skip', '!clear', '!loop']:
            last5 = ''
            last5 += f'__**0.** {player.currentSong["trackName"]}__\n'
            for i, x in enumerate(player.queue[:5]):
                last5 += f'**{i+1}**- {x["trackName"]} [by: {player.currentSong["artist"]}]\n'
            player.embed.title = f'Queue: {len(player.queue)} songs.'
            player.embed.description=f'Now Playing: **{player.currentSong["trackName"]}**'
            player.embed.set_field_at(0, name='Author:', value=f'{player.currentSong["artist"]}')
            player.embed.set_field_at(1, name='Loop:', value=player.loop)
            player.embed.set_field_at(2, name='Last 5 in queue', value=f'{last5}', inline=False)
            await embedMSG.edit(embed=player.embed)
            

cmds = ['!skip', '!pause', '!shuffle', '!resume', '!stop', '!clear', '!loop', '!queue']

    # @bot.command(name='skip', aliases = ['next'])
    # async def skipTrack(ctx):
    #     player.skip()

    # @bot.command(name='pause')
    # async def pause(ctx):
    #     player.pause()

    # @bot.command(name='shuffle')
    # async def shuffle(ctx):
    #     player.shuffle()
        
    # @bot.command(name='resume')
    # async def resume(ctx):
    #     player.resume()

    # @bot.command(name='stop')
    # async def stopPlayer(ctx):
    #     await player.stop()
    #     return 0
    
    # @bot.event
    # async def on_error():
    #     player.stop()


# vc.source = discord.PCMVolumeTransformer(vc.source, 1)

