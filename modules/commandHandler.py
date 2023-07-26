from typing import Optional
import os
import discord
import random
import modules.utils as utils
from discord import app_commands
from modules.GPT import SmartDamageGPT
import modules.MortyUI as MortyUI
import sqlite3
from dataclasses import dataclass


OWNER_GUILD = discord.Object(id=os.getenv('GUILD_ID'))
BotGPT_ID = os.getenv('BOT_ID')

CoreChannelID = os.getenv('CORE_CHANNEL')
FoxDamageChannelID = os.getenv('FOX_DAMAGE_CHANNEL')

print("[MORTYBOT] Attaching Databases...")
SmartDamageDB = sqlite3.connect('SmartDamage2.db')

print("[MORTYBOT] Done!")






class MortyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=OWNER_GUILD)
        await self.tree.sync(guild=OWNER_GUILD)

intents = discord.Intents.default()
intents.message_content = True
client = MortyBot(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id}) | {len(client.guilds)} servers')
    for guild in client.guilds:
        print(f'{guild.name} (id: {guild.id})')
    print('------')

    utils.updateGuildsDB(utils.MortyBotDB, client.guilds)
    utils.Servers = utils.loadServers(utils.MortyBotDB)


    #Greetings
    morty_greetings = [
        "Uh, he-hey there, everybody!",
        "W-whoa, h-hello, Discord world!",
        "Um, h-hiya! Morty bot is here!",
        "Oh geez, h-hello everyone!",
        "H-hey, uh, what's up, Discord pals?",
        "A-a-a-hey, nice to meet you all!",
        "G-greetings, fellow Discord adventurers!",
        "H-hi there, partners in chat!",
        "Hey, um, how's it going, Discord universe?",
        "Oh man, h-hello! Morty bot reporting for duty!"
    ]

    #Send greetings to all configured servers
    for server in utils.Servers:
        if(server.ISCONFIGURED == True and server.CORE_CHANNEL != 0):
            core_channel = await client.fetch_channel(server.CORE_CHANNEL)
            random_greeting = random.choice(morty_greetings)
            await core_channel.send(random_greeting)
        else:
            print(f"Server {server.GUILD_ID} ({server.GUILD_NAME}) is not configured!")


@client.tree.command()
async def ping(interaction: discord.Interaction):
    """A simple ping command"""
    await interaction.response.send_message('Pong!')






#Setup command
@client.tree.command()
async def setup(interaction: discord.Interaction):
    """Setup the bot"""
    view = MortyUI.SetupView(sql=utils.MortyBotDB, guild=interaction.guild)
    await interaction.response.send_message("Choose an option to configure:", view=view)







@client.tree.command()
async def chat(interaction: discord.Interaction, message: str):
    """Chat with the bot"""
    await interaction.response.send_message(interaction.user.name +' said: ' + message)

@client.event
async def on_message(message: discord.Message):
    print(f"[MSG] From: [{message.author.name}] ChannelID: [{message.channel.id}] Content: [{message.content}]")

    if message.content.startswith(BotGPT_ID):
        await message.channel.send('Hello!')
    


    #If message is in Smart Damage Channel process it
    if message.channel.id == int(FoxDamageChannelID) and message.author.id != int(BotGPT_ID):
        print("Smart Damage Question")
        async with message.channel.typing():
            #await message.reply(getRequiredMunitions(SmartDamageDB, SmartDamageGPT(message.content)))
            await message.reply(SmartDamageGPT(SmartDamageDB,message.content))


