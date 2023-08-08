import aiosqlite
import json




#This function is called by GPT to get the number of rounds needed to destroy a target
async def get_rounds_needed(sql: aiosqlite.Connection, target: str, ammo: str, tier: int=0) -> json:

    #Build the query based on the parameters given
    if tier > 0:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" AND SmartDamage.tier = '+str(tier) + ' COLLATE NOCASE'
    else:
        query = 'SELECT "'+ammo+'", Name, Tier FROM SmartDamage WHERE SmartDamage.target LIKE "%'+target+',%" COLLATE NOCASE'
        
    #Print the query for debugging
    print("[SQL Q] "+ query)

    #Execute the query
    async with sql.cursor() as cursor:
        await cursor.execute(query)
        row = await cursor.fetchone()
    
    #get tier from the query
    if row is not None:
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
    else:
        return json.dumps({"error": "No results found"})