import openai
import os
import re
# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')


def SmartDamageGPT(question):
    systemGPT = [
    {"role": "system", "content" : "The user will prompt the system with a question. you will break the question down to its core and output json as the following: 'how many fire rockets to destroy tier 1 Town Base' response: '{'type':'FireRocket', 'target':'TownBase' , 'tier': 1}'"},
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