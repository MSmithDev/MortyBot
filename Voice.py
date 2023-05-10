from elevenlabslib import *
from elevenlabslib.helpers import *


def VoiceSetup(key: str) -> bool:
    global e11Voice, e11Voices
    e11Voice = ElevenLabsUser(key)

    # Get the voices from ElevenLabs (replace with your own voices)
    e11Voices = {
        "DuckyJr":e11Voice.get_voices_by_name("DuckyJR2")[0], 
        "Cortana":e11Voice.get_voices_by_name("Cortana")[0],
        }
    e11Voice = e11Voices["DuckyJr"] # set default voice

    return True

def VoiceChange(voice: str) -> bool:
    global e11Voice
    e11Voice = e11Voices[voice]
    return True

def VoiceList() -> list:
    return list(e11Voices.keys())
