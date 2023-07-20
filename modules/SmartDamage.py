import sqlite3
import json


def getRequiredMunitions(sql, GPTResponse):
    print("[SmartDamage] GPTResponse: ["+GPTResponse+"]")
    request = json.loads(GPTResponse)
    ammo = request['type']
    target = request['target']
    try:
        tier = request['tier']
    except:
        tier = 0

    if tier > 0:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" AND SmartDamage.tier = '+str(tier) + ' COLLATE NOCASE'
    else:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" COLLATE NOCASE'
        
   
    print("[SQL Q] "+ query)
    cursor = sql.cursor()
    cursor.execute(query)
    row = cursor.fetchone()

    ds = "Prompt:```" + GPTResponse + "```\n"
    ds += "Query: ```" + query + "```\n"
    
    tier = row[2]

    if tier > 0:
        ds += f"Answer: ```It will take {row[0]} {ammo} to destroy a Tier {tier} {row[1]}```"
    else:
        ds += f"Answer: ```It will take {row[0]} {ammo} to destroy a {row[1]}```"

    return ds