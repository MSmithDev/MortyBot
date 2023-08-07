import tiktoken
import aiosqlite
from dataclasses import dataclass
from enum import Enum
from typing import List



# Function to check the number of tokens in a message
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
def checkTokenCount(input: str) -> int:
    print("Checking tokens...")
    num_tokens = len(encoding.encode(input))
    return num_tokens

@dataclass
class ServerConfig:
    GUILD_ID: int
    GUILD_NAME: str
    CORE_CHANNEL: int
    SMARTDAMAGE_CHANNEL: int
    FOXSTORAGE_CHANNEL: int
    VOICECREATE_CHANNEL: int
    VOICESTORAGE_CHANNEL: int
    ISCONFIGURED: bool


Servers: List[ServerConfig] = []

async def updateServerList():
    global Servers
    Servers = await loadServers(MortyBotDB)



class ChannelNames(Enum):
    CORE_CHANNEL = "CORE_CHANNEL"
    SMARTDAMAGE_CHANNEL = "SMARTDAMAGE_CHANNEL"
    FOXSTORAGE_CHANNEL = "FOXSTORAGE_CHANNEL"
    VOICECREATE_CHANNEL = "VOICECREATE_CHANNEL"
    VOICESTORAGE_CHANNEL = "VOICESTORAGE_CHANNEL"
    ISCONFIGURED = "ISCONFIGURED"

async def updateGuildsDB(sql, guilds):
    #Get the servers from the database
    query = 'SELECT * FROM Config'
    async with sql.cursor() as cursor:
        await cursor.execute(query)
        rows = await cursor.fetchall()

    #Create a list of servers
    servers = []
    for row in rows:
        servers.append(ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

    #Check if the server exists in the database, if not add it
    for guild in guilds:
        guildExists = False
        for server in servers:
            if guild.id == server.GUILD_ID:
                guildExists = True
                # Check if the name has changed
                if guild.name != server.GUILD_NAME:
                    print(f"[Utils] Updating server name in database: {guild.id} ({guild.name})")
                    query = 'UPDATE Config SET GUILD_NAME = ? WHERE GUILD_ID = ?'
                    async with sql.cursor() as cursor:
                        cursor.execute(query, (guild.name, guild.id))
                    await sql.commit()
                break
        if not guildExists:
            print(f"[Utils] Adding new server to database: {guild.name} ({guild.id})")
            query = 'INSERT INTO Config (GUILD_ID, GUILD_NAME, CORE_CHANNEL, SMARTDAMAGE_CHANNEL, FOXSTORAGE_CHANNEL, VOICECREATE_CHANNEL, VOICESTORAGE_CHANNEL, ISCONFIGURED) VALUES ('+str(guild.id)+', "'+guild.name+'", 0, 0, 0, 0, 0, 0)'
            async with sql.cursor() as cursor:
                await cursor.execute(query)
            await sql.commit()

    #TODO: Implement this when ready.
    #Check if the server has been removed from the guilds, if so remove it from the database
    #for server in servers:
    #    guildExists = False
    #    for guild in guilds:
    #        if guild.id == server.GUILD_ID:
    #            guildExists = True
    #            break
    #    if not guildExists:
    #        query = 'DELETE FROM Config WHERE GUILD_ID = '+str(server.GUILD_ID)
    #        async with sql.cursor() as cursor
    #        await cursor.execute(query)
    #        await sql.commit()

async def loadServers(sql):
    #Get the servers from the database
    query = 'SELECT * FROM Config'
    async with sql.cursor() as cursor:
        await cursor.execute(query)
        rows = await cursor.fetchall()

    #Create a list of servers
    servers = []
    for row in rows:
        servers.append(ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

    #Return the list of servers
    return servers

async def loadServer(sql, guild):
    #Get the servers from the database
    query = 'SELECT * FROM Config WHERE GUILD_ID = '+str(guild)
    async with sql.cursor() as cursor:
        await cursor.execute(query)
        row = await cursor.fetchone()

    #Create a server
    server = ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])

    #Return the server
    return server

async def saveChannel(sql, guild, channelname, id):
    query = f'UPDATE Config SET `{channelname}` = {id} WHERE GUILD_ID = {guild}'
    print(f"[Utils] Saving channel {channelname} ({id}) for guild {guild} using query {query}")
    async with sql.cursor() as cursor:

        #try to execute the query return false if it fails
        try:
            await cursor.execute(query)
            await sql.commit()

            return True
        except Exception as error:
            #print exception
            print(f"[Utils] Error saving channel: {error}")
            return False
    
async def setConfigured(sql, guild):
    query = f'UPDATE Config SET `ISCONFIGURED` = 1 WHERE GUILD_ID = {guild}'
    print(f"[Utils] Setting guild {guild} as configured using query {query}")
    async with sql.cursor() as cursor:

        #try to execute the query return false if it fails
        try:
            await cursor.execute(query)
            await sql.commit()

            return True
        except:
            return False
    
async def resetConfig(sql, guild):
    query = f'UPDATE Config SET `ISCONFIGURED` = 0, `CORE_CHANNEL` = 0, `SMARTDAMAGE_CHANNEL` = 0, `FOXSTORAGE_CHANNEL` = 0, `VOICECREATE_CHANNEL` = 0, `VOICESTORAGE_CHANNEL` = 0 WHERE GUILD_ID = {guild}'
    print(f"[Utils] Resetting guild {guild} using query {query}")
    
    #try to execute the query return false if it fails
    try:
        async with sql.cursor() as cursor:
            await cursor.execute(query)
        await sql.commit()

        return True
    except:
        return False
