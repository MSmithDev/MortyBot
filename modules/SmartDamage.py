import sqlite3
import json




#This function is called by GPT to get the number of rounds needed to destroy a target
def get_rounds_needed(sql, target, ammo, tier=0):

    #Build the query based on the parameters given
    if tier > 0:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" AND SmartDamage.tier = '+str(tier) + ' COLLATE NOCASE'
    else:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" COLLATE NOCASE'
        
    #Print the query for debugging
    print("[SQL Q] "+ query)

    #Execute the query
    cursor = sql.cursor()
    cursor.execute(query)

    #Get the results
    row = cursor.fetchone()

    #get tier from the query
    tier = row[2]

    #if the tier is greater than 0, then we need to return the tier
    if (tier > 0):
        response = {
                "target": row[1],
                "ammo": ammo,
                "Tier": tier,
                "needed": row[0],
            }
    else:
        response = {
            "target": row[1],
            "ammo": ammo,
            "needed": row[0],
        }

    #return the response as a JSON string
    return json.dumps(response)