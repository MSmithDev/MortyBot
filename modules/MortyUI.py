import discord
import modules.utils as utils
from discord.ext import commands


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
            utils.resetConfig(self.sql, self.guild.id)
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content="Reset!",view=view)

        async def doneCallback(interaction: discord.Interaction):
            print("[MortyUI] Done Button Clicked")
            utils.setConfigured(self.sql, self.guild.id)
            utils.updateServerList()
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

    async def on_timeout(interaction: discord.Interaction):
        print("[MortyUI] Timed Out")
        try:
            await interaction.message.edit(view=None)
        except discord.NotFound:
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
    