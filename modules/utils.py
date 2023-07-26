import tiktoken
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import List

MortyBotDB = sqlite3.connect('MortyBot.db')

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
    VOICECREATE_CHANNEL: int
    VOICESTORAGE_CHANNEL: int
    ISCONFIGURED: bool


Servers: List[ServerConfig] = []

def updateServerList():
    global Servers
    print("[MORTYBOT] PRE Updating Server List...")
    print(Servers)
    Servers = loadServers(MortyBotDB)
    print("[MORTYBOT] POST Updating Server List...")
    print(Servers)
    print("DONE!")


class ChannelNames(Enum):
    CORE_CHANNEL = "CORE_CHANNEL"
    SMARTDAMAGE_CHANNEL = "SMARTDAMAGE_CHANNEL"
    VOICECREATE_CHANNEL = "VOICECREATE_CHANNEL"
    VOICESTORAGE_CHANNEL = "VOICESTORAGE_CHANNEL"
    ISCONFIGURED = "ISCONFIGURED"

def updateGuildsDB(sql, guilds):
    #Get the servers from the database
    query = 'SELECT * FROM Config'
    cursor = sql.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    #Create a list of servers
    servers = []
    for row in rows:
        servers.append(ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

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
                    cursor = sql.cursor()
                    cursor.execute(query, (guild.name, guild.id))
                    sql.commit()
                break
        if not guildExists:
            print(f"[Utils] Adding new server to database: {guild.name} ({guild.id})")
            query = 'INSERT INTO Config (GUILD_ID, GUILD_NAME, CORE_CHANNEL, SMARTDAMAGE_CHANNEL, VOICECREATE_CHANNEL, VOICESTORAGE_CHANNEL, ISCONFIGURED) VALUES ('+str(guild.id)+', "'+guild.name+'", 0, 0, 0, 0, 0)'
            cursor = sql.cursor()
            cursor.execute(query)
            sql.commit()

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
    #        cursor = sql.cursor()
    #        cursor.execute(query)
    #        sql.commit()

def loadServers(sql):
    #Get the servers from the database
    query = 'SELECT * FROM Config'
    cursor = sql.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    #Create a list of servers
    servers = []
    for row in rows:
        servers.append(ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

    #Return the list of servers
    return servers

def loadServer(sql, guild):
    #Get the servers from the database
    query = 'SELECT * FROM Config WHERE GUILD_ID = '+str(guild)
    cursor = sql.cursor()
    cursor.execute(query)
    row = cursor.fetchone()

    #Create a server
    server = ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6])

    #Return the server
    return server

def saveChannel(sql, guild, channelname, id):
    query = f'UPDATE Config SET `{channelname}` = {id} WHERE GUILD_ID = {guild}'
    print(f"[Utils] Saving channel {channelname} ({id}) for guild {guild} using query {query}")
    cursor = sql.cursor()

    #try to execute the query return false if it fails
    try:
        cursor.execute(query)
        sql.commit()

        return True
    except:
        return False
    
def setConfigured(sql, guild):
    query = f'UPDATE Config SET `ISCONFIGURED` = 1 WHERE GUILD_ID = {guild}'
    print(f"[Utils] Setting guild {guild} as configured using query {query}")
    cursor = sql.cursor()

    #try to execute the query return false if it fails
    try:
        cursor.execute(query)
        sql.commit()

        return True
    except:
        return False
    
def resetConfig(sql, guild):
    query = f'UPDATE Config SET `ISCONFIGURED` = 0, `CORE_CHANNEL` = 0, `SMARTDAMAGE_CHANNEL` = 0, `VOICECREATE_CHANNEL` = 0, `VOICESTORAGE_CHANNEL` = 0 WHERE GUILD_ID = {guild}'
    print(f"[Utils] Resetting guild {guild} using query {query}")
    
    #try to execute the query return false if it fails
    try:
        cursor = sql.cursor()
        cursor.execute(query)
        sql.commit()

        return True
    except:
        return False
