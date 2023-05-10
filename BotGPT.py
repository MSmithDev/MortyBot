import openai
import discord
import os
import Personality
from modules import utils
from modules.commandHandler import client
import Voice

# check if the .env has elevenlabs api key
if os.getenv('ELEVENLABS_API_KEY'):
    ElevenLabsKey = os.getenv('ELEVENLABS_API_KEY')
    Voice.VoiceSetup(ElevenLabsKey)



# check if the .env has elevenlabs api key
if os.getenv('ELEVENLABS_API_KEY'):
    from elevenlabslib import *
    from elevenlabslib.helpers import *
    
    e11Voice = ElevenLabsUser(ElevenLabsKey)

    # Get the voices from ElevenLabs (replace with your own voices)
    e11Voices = {
        "DuckyJr":e11Voice.get_voices_by_name("DuckyJR2")[0], 
        "Cortana":e11Voice.get_voices_by_name("Cortana")[0],
        }
    e11Voice = e11Voices["DuckyJr"] # set default voice

# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')
discord_token = os.getenv('DISCORD_TOKEN')
BotGPT_ID = os.getenv('BOT_ID')

# Check if main variables are set
if not openai.api_key:
    raise Exception("OPENAI_API_KEY is not set")
if not discord_token:
    raise Exception("DISCORD_TOKEN is not set")
if not BotGPT_ID:
    raise Exception("BOT_ID is not set")

client.run(discord_token)