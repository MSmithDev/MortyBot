import discord
import modules.utils as utils
from discord.ext import commands
import logging

logger = logging.getLogger("mortybot")
#Configuration View
class SetupView(discord.ui.View):
    
    def __init__(self, sql, guild):
        super().__init__(timeout=None)
        self.server = None
        self.guild = guild
        self.sql = sql
        
    

    async def initialize(self):
        self.server = await utils.loadServer(self.sql, self.guild.id)
        self.add_buttons()

    @classmethod
    async def create(cls, sql, guild):
        view = cls(sql, guild)
        await view.initialize()
        return view

    def buttonState(self, state):
  
        if(state == 0):
            return discord.ButtonStyle.red
        else:
            return discord.ButtonStyle.green

    def add_buttons(self):
        core = discord.ui.Button(label='Core Channel', style=self.buttonState(self.server.CORE_CHANNEL),row=0)
        smartDamage = discord.ui.Button(label='SmartDamage Channel', style=self.buttonState(self.server.SMARTDAMAGE_CHANNEL),row=0)
        foxStorage = discord.ui.Button(label='FoxStorage Channel', style=self.buttonState(self.server.FOXSTORAGE_CHANNEL),row=0)
        voiceCreate = discord.ui.Button(label='VoiceCreate Channel', style=self.buttonState(self.server.VOICECREATE_CHANNEL),row=0)
        voiceStorage = discord.ui.Button(label='VoiceStorage Channel', style=self.buttonState(self.server.VOICESTORAGE_CHANNEL),row=0)

        doneButton = discord.ui.Button(label='Done', style=discord.ButtonStyle.blurple,row=2)
        resetButton = discord.ui.Button(label='Reset', style=discord.ButtonStyle.danger,row=2)

        #Config Channels
        message = "Please select a channel or start typing it to search"
        async def coreCallback(interaction: discord.Interaction):
            print("[MortyUI] Core Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.CORE_CHANNEL.value)
            await interaction.response.edit_message(content=message,view=view)

        async def smartDamageCallback(interaction: discord.Interaction):
            print("[MortyUI] SmartDamage Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.SMARTDAMAGE_CHANNEL.value)
            await interaction.response.edit_message(content=message,view=view)
            
        async def foxStorageCallback(interaction: discord.Interaction):
            print("[MortyUI] FoxStorage Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.FOXSTORAGE_CHANNEL.value)
            await interaction.response.edit_message(content=message,view=view)
        
        async def voiceCreateCallback(interaction: discord.Interaction):
            print("[MortyUI] VoiceCreate Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.VOICECREATE_CHANNEL.value)
            await interaction.response.edit_message(content=message,view=view)
        
        async def voiceStorageCallback(interaction: discord.Interaction):
            print("[MortyUI] VoiceStorage Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.VOICESTORAGE_CHANNEL.value)
            await interaction.response.edit_message(content=message,view=view)



        #Reset and Done Buttons
        async def resetCallback(interaction: discord.Interaction):
            print("[MortyUI] Reset Button Clicked")
            await utils.resetConfig(self.sql, self.guild.id)
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content="Reset!",view=view)

        async def doneCallback(interaction: discord.Interaction):
            print("[MortyUI] Done Button Clicked")
            await utils.setConfigured(self.sql, self.guild.id)
            await utils.updateServerList()
            await interaction.response.edit_message(content="Done!",view=None)

        core.callback = coreCallback
        smartDamage.callback = smartDamageCallback
        foxStorage.callback = foxStorageCallback
        voiceCreate.callback = voiceCreateCallback
        voiceStorage.callback = voiceStorageCallback

        doneButton.callback = doneCallback
        resetButton.callback = resetCallback

        self.add_item(core)
        self.add_item(smartDamage)
        self.add_item(foxStorage)
        self.add_item(voiceCreate)
        self.add_item(voiceStorage)

        self.add_item(doneButton)
        self.add_item(resetButton)

    async def on_timeout(self):
        print("[MortyUI] Timed Out")
        try:
            await self.message.edit(view=None)
        except Exception as e:
            pass
            

#UpdateChannelConfig View
class UpdateChannelConfigView(discord.ui.View):

    def __init__(self, sql, guild,channel):
        super().__init__(timeout=None)
        self.sql = sql
        self.guild = guild
        self.channel = channel
        self.add_buttons()
        
    @discord.ui.channel_select(
        placeholder="Select a channel",
        min_values=1,
        max_values=1,
        row=0,
        channel_types=[discord.ChannelType.text,discord.ChannelType.private]
    )
    async def select_callback(self, select, interaction):
        print(f"[MortyUI] Selector Choice: {select.values[0].id} ({select.values[0]})")
        print(f"[MortyUI] Channel: {self.channel}")
        #save the channel to the database
        res = await utils.saveChannel(self.sql, self.guild.id,self.channel ,select.values[0].id)
        print(f"[MortyUI] Save Result: {res}")
        if(res):
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content=f"Successfully updated, any other changes?",view=view)

    def add_buttons(self):
        
        cancel = discord.ui.Button(label='Cancel', style=discord.ButtonStyle.red, row=1)

        async def cancelCallback(interaction: discord.Interaction):
            print("Cancel Button Clicked")
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content="Choose an option to configure:",view=view)
    
        cancel.callback = cancelCallback
        self.add_item(cancel)
    

    #Stockpile edit buttons
class StockpileEditButtons(discord.ui.View):

    def __init__(self, sql, guild,channel):
        super().__init__(timeout=None)
        self.sql = sql
        self.guild = guild
        self.channel = channel
        self.add_buttons()

    def add_buttons(self):
        
        cancel = discord.ui.Button(label='Cancel', style=discord.ButtonStyle.red, row=1)

        async def cancelCallback(interaction: discord.Interaction):
            print("Cancel Button Clicked")
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content="Choose an option to configure:",view=view)
    
        cancel.callback = cancelCallback
        self.add_item(cancel)



#Voice interaction view
class VoiceResponseUI(discord.ui.View):

    def __init__(self, guild, channel):
        super().__init__(timeout=None)
        self.guild = guild
        self.recordState = False
        self.voiceClient: discord.VoiceClient = None
        self.connections = {}
        self.add_buttons()
    
    def add_buttons(self):

        join = discord.ui.Button(label='Join', style=discord.ButtonStyle.green, row=0)
        leave = discord.ui.Button(label='Leave', style=discord.ButtonStyle.red, row=0)

        start = discord.ui.Button(label='Start', style=discord.ButtonStyle.green, row=1, emoji="⏺")
        stop = discord.ui.Button(label='Stop', style=discord.ButtonStyle.red, row=1, emoji="⏹")

        #Join Button
        async def join_callback(interaction: discord.Interaction):
            logger.debug(f"[MortyUI] [VoiceResponse] Join Button Clicked")
            logger.debug(f"[MortyUI] [VoiceResponse] User: {interaction.user}")
            logger.debug(f"[MortyUI] [VoiceResponse] voice: {interaction.user.voice}")

            if interaction.user.voice is None:
                logger.warn(f"[MortyUI] [VoiceResponse] User is not in a voice channel")
                await interaction.response.edit_message(content="You are not in a voice channel!")

            else:
                logger.debug(f"[MortyUI] [VoiceResponse] Attempting to join {interaction.user.voice.channel}")
                await interaction.response.edit_message(content="Joining!")
                if interaction.guild.voice_client is not None:
                    logger.debug(f"[MortyUI] [VoiceResponse] Already in a voice channel, disconnecting")
                    await interaction.guild.voice_client.disconnect()
                self.voiceClient = await interaction.user.voice.channel.connect()

        #Leave Button
        async def leave_callback(interaction: discord.Interaction):
            logger.debug(f"[MortyUI] [VoiceResponse] Leave Button Clicked")

            if interaction.guild.voice_client is None:
                logger.warn(f"[MortyUI] [VoiceResponse] MortyBot is not in a voice channel")
                await interaction.response.edit_message(content="MortyBot is not in a voice channel!")

            else:
                logger.debug(f"[MortyUI] [VoiceResponse] Attempting to leave {interaction.guild.voice_client.channel}")
                await interaction.response.edit_message(content="Leaving!")
                if interaction.guild.voice_client is not None:
                    logger.debug(f"[MortyUI] [VoiceResponse] Already in a voice channel, disconnecting")
                    await interaction.guild.voice_client.disconnect()
                self.voiceClient = None

        async def finished_callback(sink, channel: discord.TextChannel, *args):
            recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
            files = None
            files = [
                discord.File(audio.file, f"{user_id}.{sink.encoding}")
                for user_id, audio in sink.audio_data.items()
            ]
            print("RECORDED USERS")
            print(recorded_users)
            print("FILES")
            print(files)

            


            if len(files) == 0:
                await channel.send("No users recorded!")
            else:

                #Save the files to the tempvoice folder
                for user_id, audio in sink.audio_data.items():
                    with open(f"./tempvoice/{user_id}.mp3", "wb") as f:
                        f.write(audio.file.getbuffer())

                #Send the files to the channel
                await channel.send(
                    f"Recorded {len(recorded_users)} users: {', '.join(recorded_users)}", files=files
                )

            
            

        #Start Button
        async def start_callback(interaction: discord.Interaction):
            logger.debug((f"[MortyUI] [VoiceResponse] Start Button Clicked"))
            self.recordState = True
            await interaction.response.edit_message(content="Started! Recording...")

            voiceTarget = interaction.user
            logger.debug(f"[MortyUI] [VoiceResponse] voiceTarget: {voiceTarget.name}")

            self.connections.update({interaction.guild.id: self.voiceClient})
            mysink = discord.sinks.mp3.MP3Sink()

            self.voiceClient.start_recording(
                mysink,
                finished_callback,
                interaction.channel
            )

        #Stop Button
        async def stop_callback(interaction: discord.Interaction):
            logger.debug((f"[MortyUI] [VoiceResponse] Stop Button Clicked"))
            self.recordState = False
            await interaction.response.edit_message(content="Stopped! Processing audio...")

            if self.voiceClient.recording:
                self.voiceClient.stop_recording()
                

        #Register callbacks
        join.callback = join_callback
        leave.callback = leave_callback
        start.callback = start_callback
        stop.callback = stop_callback

        #add items to view
        self.add_item(join)
        self.add_item(leave)
        self.add_item(start)
        self.add_item(stop)