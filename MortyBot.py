import os
from modules import utils
from modules.commandHandler import client
import Voice


# check if the .env has elevenlabs api key
if os.getenv('ELEVENLABS_API_KEY'):
    ElevenLabsKey = os.getenv('ELEVENLABS_API_KEY')
    Voice.VoiceSetup(ElevenLabsKey)


discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)

