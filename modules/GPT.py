import json
import openai
import os
import re
from modules.SmartDamage import get_rounds_needed
# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')


SmartDamagaMsgs = [{"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Names of targets and weapons are from the game Foxhole. Tiers can be represented as Tier 1,2,3 or t1,t2,t3. Remove spaces from target names and do not include the tier. Ammo types: [12.7mm,Mammon,Tremola,30mm,RPG,40mm,75mm,FireRocket,Mortar,HERocket,120mm,150mm,300mm,Ignifist,APRPG,68mm,ARCRPG,94.5mm,Satchel,Hydra,250mm,Havoc] an example would be 'How many 150mm to kill a t3 relic base' 150mm is the ammo, t3 is tier 3, and relic base is the target."}]

def SmartDamageGPT(sql,question):

    print(f"[GPT] querySmartDamage: {question}")
    SmartDamagaMsgs.append({"role": "user", "content": question})
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
            messages=SmartDamagaMsgs,
            functions=functions,
            function_call="auto",
            #function_call={"name": "get_rounds_needed"}  # auto is default, but we'll be explicit
        )
    response_message = response.choices[0].message
    
    #Add the response to the messages list
    SmartDamagaMsgs.append(response_message)


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
        function_response = fuction_to_call(
            sql=sql,
            target=function_args.get("target"),
            ammo=function_args.get("ammo"),
            tier=function_args.get("tier",0),
        )

        # Step 4: send the info on the function call and function response to GPT
        SmartDamagaMsgs.append(response_message)  # extend conversation with assistant's reply
        SmartDamagaMsgs.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=SmartDamagaMsgs,
        )  # get a new response from GPT where it can see the function response
        second_response_msg = second_response.choices[0].message
        print("[GPT] Response after function: "+second_response_msg.content)
        SmartDamagaMsgs.append(second_response_msg)
        return second_response_msg.content
    else:
        return response_message.content