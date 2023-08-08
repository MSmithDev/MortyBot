from typing import Optional
import os
import discord
from discord.ext import commands
import random
import modules.utils as utils
from modules.GPT import SmartDamageGPT
from modules.SmartStockpile import getGuildStockpiles, makeStockpileEmbeds
import modules.MortyUI as MortyUI
import aiosqlite 
from dataclasses import dataclass
import asyncio
import Voice

discord_token = os.getenv('DISCORD_TOKEN')

# check if the .env has elevenlabs api key
if os.getenv('ELEVENLABS_API_KEY'):
    ElevenLabsKey = os.getenv('ELEVENLABS_API_KEY')
    if ElevenLabsKey is not None:
        Voice.VoiceSetup(ElevenLabsKey)
    else:
        raise ValueError('ELEVENLABS_API_KEY is not set in .env')
    
OWNER_GUILD_ID = os.getenv('GUILD_ID')
if OWNER_GUILD_ID is not None:
    OWNER_GUILD = discord.Object(id=OWNER_GUILD_ID)
else:
    raise ValueError('OWNER_GUILD is not set in .env')


BotGPT_ID = os.getenv('BOT_ID', '0')
if BotGPT_ID is '0':
    raise ValueError('BOT_ID is not set in .env')

CoreChannelID = os.getenv('CORE_CHANNEL', '0')
FoxDamageChannelID = os.getenv('FOX_DAMAGE_CHANNEL', '0')

SmartDamageDB = None
MortyBotDB = None

MortyBot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=discord.Intents.all()
)


@MortyBot.event
async def on_ready():
    print("[MORTYBOT] Attaching Databases...")
    global SmartDamageDB
    global MortyBotDB
    SmartDamageDB = await aiosqlite.connect('SmartDamage.db')
    MortyBotDB = await aiosqlite.connect('MortyBot.db')
    print("[MORTYBOT] Done!")

    print(f'Logged in as {MortyBot.user} (ID: {MortyBot.user.id}) | {len(MortyBot.guilds)} servers')
    for guild in MortyBot.guilds:
        print(f'{guild.name} (id: {guild.id})')
    print('------')

    await utils.updateGuildsDB(MortyBotDB, MortyBot.guilds)
    utils.Servers = await utils.loadServers(MortyBotDB)


    #Greetings
    morty_greetings = [
        "Uh, he-hey there, everybody!",
        "W-whoa, h-hello, Discord world!",
        "Um, h-hiya! Morty bot is here!",
        "Oh geez, h-hello everyone!",
        "H-hey, uh, what's up, Discord pals?",
        "A-a-a-hey, nice to meet you all!",
        "G-greetings, fellow Discord adventurers!",
        "H-hi there, partners in chat!",
        "Hey, um, how's it going, Discord universe?",
        "Oh man, h-hello! Morty bot reporting for duty!"
    ]

    #Send greetings to all configured servers
    for server in utils.Servers:
        if(server.ISCONFIGURED == True and server.CORE_CHANNEL != 0):
            core_channel = await MortyBot.fetch_channel(server.CORE_CHANNEL)
            random_greeting = random.choice(morty_greetings)
            await core_channel.send(random_greeting)
        else:
            print(f"Server {server.GUILD_ID} ({server.GUILD_NAME}) is not configured!")



#Setup MortyBot Channels
@MortyBot.slash_command(name="setup", description="Setup MortyBot for your server")
async def setup(interaction: discord.Interaction):
    """Setup the bot"""
    view = await MortyUI.SetupView.create(sql=MortyBotDB, guild=interaction.guild)
    await interaction.response.send_message("Choose an option to configure:", view=view,ephemeral=True)



@MortyBot.slash_command(name="teststockpile", description="Test Stockpile")
async def stockpile(interaction: discord.Interaction):
    """Stockpile Test Command"""
    
    if interaction.guild is not None:
        test = await getGuildStockpiles(MortyBotDB, interaction.guild.id)
        test2 = await makeStockpileEmbeds(test,channel=interaction.channel)

    else:
        raise ValueError('Interaction Guild is None')


    #await interaction.response.send_message("[SmartStockpile] Check print output")



@MortyBot.event
async def on_message(message: discord.Message):
    print(f"[MSG] From: [{message.author.name}] ChannelID: [{message.channel.id}] Content: [{message.content}]")

    if message.content.startswith(BotGPT_ID):
        await message.channel.send('Hello!')
    


    #If message is in Smart Damage Channel process it
    if message.channel.id == int(FoxDamageChannelID) and message.author.id != int(BotGPT_ID):
        print("Smart Damage Question")
        async with message.channel.typing():
            #await message.reply(getRequiredMunitions(SmartDamageDB, SmartDamageGPT(message.content)))
            await message.reply(SmartDamageGPT(SmartDamageDB,message.content))


MortyBot.run(discord_token)