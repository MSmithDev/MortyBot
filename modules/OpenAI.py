import json
import aiosqlite
import openai
import os
import re
from modules.SmartDamage import get_rounds_needed
import logging
import Persona
import discord
from elevenlabslib import *
from elevenlabslib.helpers import *
import requests
import asyncio
import time
import modules.GPTFunctions as GPTFunctions

#setup logging
logger = logging.getLogger("mortybot")

# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')


SmartDamageMsgs = [{"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Names of targets and weapons are from the game Foxhole. Tiers can be represented as Tier 1,2,3 or t1,t2,t3. Remove spaces from target names and do not include the tier. Ammo types: [12.7mm,Mammon,Tremola,30mm,RPG,40mm,75mm,FireRocket,Mortar,HERocket,120mm,150mm,300mm,Ignifist,APRPG,68mm,ARCRPG,94.5mm,Satchel,Hydra,250mm,Havoc] an example would be 'How many 150mm to kill a t3 relic base' 150mm is the ammo, t3 is tier 3, and relic base is the target."}]

async def SmartDamageGPT(sql: aiosqlite.Connection, question: str):

    print(f"[GPT] querySmartDamage: {question}")
    SmartDamageMsgs.append({"role": "user", "content": question})
    functions = [
        {
            "name": "get_rounds_needed",
            "description": "Get the number of rounds needed to destroy/kill a target",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Type of structure to destroy",
                    },
                    "ammo": {
                        "type": "string",
                        "description": "Type of ammunition to use",
                    },
                    "tier": {
                        "type": "integer",
                        "description": "Tier of structure if applicable",
                    },
                },
                "required": ["target", "ammo"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=SmartDamageMsgs,
            functions=functions,
            function_call="auto",
            #function_call={"name": "get_rounds_needed"}  # auto is default, but we'll be explicit
        )
    response_message = response.choices[0].message
    
    #Add the response to the messages list
    SmartDamageMsgs.append(response_message)


    print("[GPT] Response: ",response_message)

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_rounds_needed": get_rounds_needed,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = await fuction_to_call(
            sql=sql,
            target=function_args.get("target"),
            ammo=function_args.get("ammo"),
            tier=function_args.get("tier",0),
        )

        # Step 4: send the info on the function call and function response to GPT
        SmartDamageMsgs.append(response_message)  # extend conversation with assistant's reply
        SmartDamageMsgs.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=SmartDamageMsgs,
        )  # get a new response from GPT where it can see the function response
        second_response_msg = second_response.choices[0].message
        print("[GPT] Response after function: "+second_response_msg.content)
        SmartDamageMsgs.append(second_response_msg)
        return second_response_msg.content
    else:
        return response_message.content
    

async def whisperProcess(file: str) -> str:

    audio_file = open(file, "rb")

    if audio_file is None:
        logger.warning(f"[OpenAI] File not found: {file}")
        return None
    
    else:

        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        logger.debug(f"[OpenAI] Transcript: {transcript}")

        return transcript




e11key = os.getenv('ELEVENLABS_API_KEY')
print("Got key: " + e11key)
user = ElevenLabsUser(e11key)
MortyVoice = user.get_voices_by_name("Matt")[0]
currentVoice = MortyVoice
messagesGPT = []

def getMessageList() -> list:
    return messagesGPT




async def sendGPTPrompt(input: str, user: discord.User, persona: Persona.Persona, interaction: discord.Interaction) -> str:
 
    #todo seperate messages for each persona
    #use a dict with persona as key and list of messages as value
    messages = persona.messages()
    messages.append({"role": "user", "name": user.name, "content": input})
    logger.debug(f"[OpenAI] Messages: {messages}")


    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-0613",
                        messages=messages,
                        functions=GPTFunctions.functions,
                        max_tokens=200,
                        temperature=0.9, #randomness of response 0-2 higher = more random
                    )
                    response_message = response.choices[0].message
                    logger.debug(f"[OpenAI] Response: {response_message}")
                    persona.add_message(response_message)
                    

                    
                    if response_message.get("function_call"):
                        logger.debug(f"[OpenAI] Function call: {response_message['function_call']}")
                        available_functions = {
                            "get_userid_in_voice": GPTFunctions.get_userid_in_voice,
                            "disconnect_user_in_voice": GPTFunctions.disconnect_user_in_voice
                        }  
                        
                        #Get function name
                        function_name = response_message["function_call"]["name"]

                        #Get function to call
                        fuction_to_call = available_functions[function_name]

                        #Get function arguments
                        function_args = json.loads(response_message["function_call"]["arguments"])

                        #Call the function
                        function_response = await fuction_to_call(
                            username=function_args.get("username"),
                            interaction=interaction
                        )
                        
                        
                        
                        return f"Function call: {response_message['function_call']}\n\n Function Response: {function_response}"
                        


                    return response_message.content
                    break
                except Exception as e:
                    logger.warning(f"[OpenAI] Error: {e}")
                    if attempt < max_retries - 1:
                        logger.warning(f"[OpenAI] Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error("[OpenAI] Failed after max retries")
                        raise e



async def sendGPTMessage(input: str, user: str,persona: Persona.Persona, voiceClient: discord.VoiceClient = None):
    
    
    messagesGPT.append(persona)

    messagesGPT.append({"role": "user", "name": user, "content": input})

    logger.debug(f"[OpenAI] Messages: {messagesGPT}")

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
                try:
                    ##If voice connected limit tokens.
                    if voiceClient is not None:
                        if voiceClient.is_connected():
                            completion = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=messagesGPT,
                            max_tokens=200,
                            temperature=1.0, #randomness of response 0-2 higher = more random
                    )
                    

                    ##Normal limit 250 tokens. Show typing indicator
                    else:
                        completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messagesGPT,
                            max_tokens=250,
                            temperature=1.0, #randomness of response 0-2 higher = more random
                        )
                    chat_response = completion.choices[0].message.content
                    messagesGPT.append({"role": "assistant", "content": chat_response})


                    ## If in voice channel speak instead of type
                    if voiceClient is not None:
                        if voiceClient.is_connected():
                            voicedata = currentVoice.generate_audio_v2(chat_response)
                            
                            save_audio_v2(voicedata[0], "speech.mp3", outputFormat="mp3")

                            voiceClient.play(discord.FFmpegPCMAudio(source="speech.mp3"))
                    else:
                        return chat_response
                    break

                except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                       return "An error occurred while communicating with the OpenAI API. Please try again later."

    pass

async def sendVoiceMessage(message: str, voiceClient: discord.VoiceClient):
    if voiceClient.is_connected():
        voicedata = currentVoice.generate_audio_bytes(message)
        save_audio_bytes(voicedata, "speech.mp3", outputFormat="mp3")

        voiceClient.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="speech.mp3"))
    else:
        logger.debug("[sendVoiceMessage] Voice not connected")
     