import sqlite3
import json


def getRequiredMunitions(sql, prompt):

    request = json.loads(prompt)
    ammo = request['type']
    target = request['target']
    try:
        tier = request['tier']
    except:
        tier = 0

    if tier > 0:
        query = 'SELECT "'+ammo+'", Name FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+'%" AND SmartDamage.tier = '+str(tier) + ' COLLATE NOCASE'
    else:
        query = 'SELECT "'+ammo+'", Name FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+'%" COLLATE NOCASE'

   
    print("[SQL Q] "+ query)
    cursor = sql.cursor()
    cursor.execute(query)
    row = cursor.fetchone()

    ds = "Prompt:```" + prompt + "```\n"
    ds += "Query: ```" + query + "```\n"
    
    if tier > 0:
        ds += f"Answer: ```It will take {row[0]} {ammo} to destroy a Tier {tier} {row[1]}```"
    else:
        ds += f"Answer: ```It will take {row[0]} {ammo} to destroy a {row[1]}```"

    return ds