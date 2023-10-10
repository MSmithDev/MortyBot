import tiktoken
import aiosqlite
import discord
from dataclasses import dataclass, field
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

async def updateServerList(sql: aiosqlite.Connection):
    global Servers
    Servers = await loadServers(sql)



class ChannelNames(Enum):
    CORE_CHANNEL = "CORE_CHANNEL"
    SMARTDAMAGE_CHANNEL = "SMARTDAMAGE_CHANNEL"
    FOXSTORAGE_CHANNEL = "FOXSTORAGE_CHANNEL"
    VOICECREATE_CHANNEL = "VOICECREATE_CHANNEL"
    VOICESTORAGE_CHANNEL = "VOICESTORAGE_CHANNEL"
    ISCONFIGURED = "ISCONFIGURED"

async def updateGuildsDB(sql: aiosqlite.Connection, guilds: List[discord.Guild]) -> bool:
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
                        await cursor.execute(query, (guild.name, guild.id))
                    await sql.commit()
                break
        if not guildExists:
            print(f"[Utils] Adding new server to database: {guild.name} ({guild.id})")
            query = 'INSERT INTO Config (GUILD_ID, GUILD_NAME, CORE_CHANNEL, SMARTDAMAGE_CHANNEL, FOXSTORAGE_CHANNEL, VOICECREATE_CHANNEL, VOICESTORAGE_CHANNEL, ISCONFIGURED) VALUES ('+str(guild.id)+', "'+guild.name+'", 0, 0, 0, 0, 0, 0)'
            async with sql.cursor() as cursor:
                await cursor.execute(query)
            await sql.commit()

    return True

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

async def loadServers(sql: aiosqlite.Connection) -> List[ServerConfig]:
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

async def loadServer(sql: aiosqlite.Connection, guild: int) -> ServerConfig:
    #Get the servers from the database
    query = 'SELECT * FROM Config WHERE GUILD_ID = '+str(guild)
    async with sql.cursor() as cursor:
        await cursor.execute(query)
        row = await cursor.fetchone()

    #Create a server if it exists
    if row is not None:
        server = ServerConfig(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        return server
    else:
        raise ValueError("Server not found in database")
    

async def saveChannel(sql: aiosqlite.Connection, guild: int, channelname: str, id: int) -> bool:
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
    
async def setConfigured(sql: aiosqlite.Connection, guild: int) -> bool:
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
    
async def resetConfig(sql: aiosqlite.Connection, guild: int) -> bool:
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

#Pad the embed title to 256 characters to force max width
def padEmbed(title: str) -> str:
    return title.ljust(60, 'ㅤ')

#create relative discord timestamp
def discordTimestamp(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"


#Misc audio

class Sinks(Enum):
    mp3 = discord.sinks.MP3Sink()
    wav = discord.sinks.WaveSink()
    pcm = discord.sinks.PCMSink()
    ogg = discord.sinks.OGGSink()
    mka = discord.sinks.MKASink()
    mkv = discord.sinks.MKVSink()
    mp4 = discord.sinks.MP4Sink()
    m4a = discord.sinks.M4ASink()


@dataclass
class linkedStockpile:
    index: int
    stockpile_id: int
    button_label: str