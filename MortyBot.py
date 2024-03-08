from typing import Optional
import os
import discord
from discord.ext import commands
from discord import option
import random
import modules.utils as utils
from modules.OpenAI import SmartDamageGPT, getMessageList, sendGPTPrompt, sendGPTMessage, sendVoiceMessage
from modules.SmartStockpile import getGuildStockpiles, makeStockpileEmbeds
import modules.MortyUI as MortyUI
import aiosqlite 
from dataclasses import dataclass
import asyncio
import Voice
from modules.Logger import setup_logger
import logging
import Persona

#setup logging
logger = setup_logger("mortybot", logging.DEBUG)
logger.info("[MortyBot] Logger setup complete")

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
if BotGPT_ID == '0':
    raise ValueError('BOT_ID is not set in .env')

CoreChannelID = os.getenv('CORE_CHANNEL', '0')
FoxDamageChannelID = os.getenv('FOX_DAMAGE_CHANNEL', '0')
FoxDamageChannelID2 = 1159922670528376973

SmartDamageDB = None
MortyBotDB = None

MortyBot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=discord.Intents.all()
)


@MortyBot.event
async def on_ready():
    logger.info("[MortyBot] Attaching Databases...")
    global SmartDamageDB
    global MortyBotDB

    #Attach databases
    SmartDamageDB = await aiosqlite.connect('SmartDamage.db')
    MortyBotDB = await aiosqlite.connect('MortyBot.db')
    
    #Log database connections
    if SmartDamageDB is not None: logger.info("[MortyBot] SmartDamageDB attached") 
    else: logger.error("[MortyBot] SmartDamageDB failed to attach")

    if MortyBotDB is not None: logger.info("[MortyBot] MortyBotDB attached")
    else: logger.error("[MortyBot] MortyBotDB failed to attach")

    logger.info("[MortyBot] Databases attached")
    logger.info("[MortyBot] ----------------------")

    #Log Server Connections
    logger.info(f'[MortyBot] Logged in as {MortyBot.user} (ID: {MortyBot.user.id}) | {len(MortyBot.guilds)} servers')

    for guild in MortyBot.guilds:
        logger.info(f'[MortyBot] {guild.name} (id: {guild.id})')
    logger.info("[MortyBot] ----------------------")
    
    logger.debug("[MortyBot] Updating Guilds DB...")
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
            logger.debug("skipping greeting TODO: fix this")
            #logger.debug(f"[MortyBot] Sending greeting to {server.GUILD_NAME} ({server.GUILD_ID})")
            #await core_channel.send(random_greeting)
        else:
            logger.warning(f"[MortyBot] Server {server.GUILD_ID} ({server.GUILD_NAME}) is not configured!")
            


#DEBUG COMMANDS
@MortyBot.slash_command(name="debug", description="debug a prompt")
@option(name="Prompt", type=str, required=True)
async def setup(interaction: discord.Interaction, input: str):
    """Debug a prompt"""
    response = await sendGPTPrompt(input=input,user=interaction.user,interaction=interaction, persona=Persona.Persona.Chat)

    await interaction.response.send_message(f"Prompt: {input}\n\n{response}",ephemeral=False)

@MortyBot.slash_command(name="msg_list", description="debug the message list")
async def setup(interaction: discord.Interaction):
    """Debug the message list"""
    
    await interaction.response.send_message(f"Msg length: {len(getMessageList())}",ephemeral=False)

#Echo to voice
@MortyBot.slash_command(name="echo", description="speak through the bot")
@option(name="message", type=str, required=True)
async def setup(interaction: discord.Interaction, message: str):
    """Speak through the bot"""
    
    await sendVoiceMessage(message=message, voiceClient=interaction.guild.voice_client)

    await interaction.response.send_message(f"Message sent to voice",ephemeral=False)
    


#Setup MortyBot Channels
@MortyBot.slash_command(name="setup", description="Setup MortyBot for your server")
async def setup(interaction: discord.Interaction):
    """Setup the bot"""
    view = await MortyUI.SetupView.create(sql=MortyBotDB, guild=interaction.guild)
    await interaction.response.send_message("Choose an option to configure:", view=view,ephemeral=True)

#VoiceControl
@MortyBot.slash_command(name="voice_cmd", description="Voice Control")
async def voice_cmd(interaction: discord.Interaction):
    """Voice Control"""

    view = MortyUI.VoiceResponseUI(guild=interaction.guild, channel=interaction.channel)
    await interaction.response.send_message("Voice Controls", view=view,ephemeral=False)


#Razz Quotes
@MortyBot.slash_command(name="words_by_razz", description="Generate a Razz Quote")
@option(name="inspire", type=str, required=False, description="Use this as inspiration")
async def setup(interaction: discord.Interaction, inspire=None):
    """Debug a prompt"""
    await interaction.response.defer()
    if inspire is None:
        inspire = "Make one quote"

    else:
        inspire = f"Make one quote using this as inspiration: '{inspire}'"
    response = await sendGPTPrompt(input=inspire,user=interaction.user,interaction=interaction, persona=Persona.Persona.Razz)

    await interaction.followup.send(response,ephemeral=True)

@MortyBot.slash_command(name="teststockpile", description="Test Stockpile")
async def stockpile(interaction: discord.Interaction):
    """Stockpile Test Command"""
    
    #remove old bot messages
    logger.debug("[MortyBot] Purging old stockpile messages...")
    await interaction.channel.purge(limit=100, check=lambda m: m.author == MortyBot.user)


    if interaction.guild is not None:
        test = await getGuildStockpiles(MortyBotDB, interaction.guild.id)
        test2 = await makeStockpileEmbeds(test,interaction=interaction)

    else:
        raise ValueError('Interaction Guild is None')

@MortyBot.slash_command(name="txt", description="send msg")
@option(name="channel", type=str, required=True)
@option(name="Prompt", type=str, required=True)
async def setup(interaction: discord.Interaction, channel: str, msg: str):
    """send msg to channel"""

    channel = await MortyBot.fetch_channel(int(channel))
    await channel.send(msg)

@MortyBot.event
async def on_message(message: discord.Message):
    print(f"[MSG] From: [{message.author.name}] ChannelID: [{message.channel.id}] Content: [{message.content}]")

    #Process messages for servers
    for server in utils.Servers:

        server_id = server.GUILD_ID
        if message.guild is not None and message.author.id != int(BotGPT_ID):
            if server_id == message.guild.id:


                #If message is in Smart Damage Channel process it
                if message.channel.id == server.SMARTDAMAGE_CHANNEL:
                    logger.debug(f"[MortyBot]({server_id}) Processing SmartDamage Message...")
                    async with message.channel.typing():
                        
                        #reply to message
                        await message.reply(await SmartDamageGPT(SmartDamageDB,message.content))
                    

                #If message is in Core Channel or tagged bot process it
                if message.channel.id == server.CORE_CHANNEL:
                    logger.debug(f"[MortyBot]({server_id}) Processing Core Message...")

                    #use typing indicator
                    async with message.channel.typing():
                        
                        #reply to message
                        await message.reply(await sendGPTMessage(input=message.content,user=message.author.name, persona=Persona.Persona.Chat.value, voiceClient=message.guild.voice_client))


MortyBot.run(discord_token)