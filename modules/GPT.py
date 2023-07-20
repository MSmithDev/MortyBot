import openai
import os
import re
# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')


def SmartDamageGPT(question):
    systemGPT = [
    {"role": "system", "content" : 'The user will prompt the system with a question. you will break the question down to its core and output json as the following: "how many fire rockets to destroy t1 Town Base" response: "{"type":"FireRocket", "target":"TownBase" , "tier": 1}" the following are the only allowed types [12.7mm,Mammon,Tremola,30mm,RPG,40mm,75mm,FireRocket,Mortar,HERocket,120mm,150mm	300mm,Ignifist,APRPG,68mm,ARCRPG,94.5mm,Satchel,Hydra,250mm,Havoc] If tier is not included in the user prompt then treat it as 0.'},
    {"role": "user", "content" : "How many 150 to kill a t3 ghouse"},
    {"role": "assistant", "content" : '{"type":"150mm", "target":"ghouse" , "tier": 3}'},
    {"role": "user", "content" : "How many 68mm to kill a RB2"},
    {"role": "assistant", "content" : '{"type":"68mm", "target":"RB2" , "tier": 2}'},
    ]

    print(f"[GPT] querySmartDamage: {question}")
    systemGPT.append({"role": "user", "content": question})
    completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=systemGPT,
                                max_tokens=250,
                                temperature=1.0, #randomness of response 0-2 higher = more random
                            )
    chat_response = completion.choices[0].message.content

    return chat_response