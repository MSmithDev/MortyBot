import discord
import modules.utils as utils
from discord.ext import commands


#Configuration View
class SetupView(discord.ui.View):
    
    def __init__(self, sql, guild):
        super().__init__(timeout=None)
        self.server = utils.loadServer(sql, guild.id)
        self.guild = guild
        self.sql = sql
        self.add_buttons()
        
    def buttonState(self, state):
  
        if(state == 0):
            return discord.ButtonStyle.red
        else:
            return discord.ButtonStyle.green

    def add_buttons(self):
        core = discord.ui.Button(label='Core Channel', style=self.buttonState(self.server.CORE_CHANNEL),row=0)
        smartDamage = discord.ui.Button(label='SmartDamage Channel', style=self.buttonState(self.server.SMARTDAMAGE_CHANNEL),row=0)
        voiceCreate = discord.ui.Button(label='VoiceCreate Channel', style=self.buttonState(self.server.VOICECREATE_CHANNEL),row=0)
        voiceStorage = discord.ui.Button(label='VoiceStorage Channel', style=self.buttonState(self.server.VOICESTORAGE_CHANNEL),row=0)

        doneButton = discord.ui.Button(label='Done', style=discord.ButtonStyle.blurple,row=2)
        resetButton = discord.ui.Button(label='Reset', style=discord.ButtonStyle.danger,row=2)

        #TODO: Add a button to reset the server config
        #Config Options
        async def coreCallback(interaction: discord.Interaction):
            print("[MortyUI] Core Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.CORE_CHANNEL.value)
            await interaction.response.edit_message(content="Please select a channel",view=view)

        async def smartDamageCallback(interaction: discord.Interaction):
            print("[MortyUI] SmartDamage Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.SMARTDAMAGE_CHANNEL.value)
            await interaction.response.edit_message(content="Please select a channel",view=view)
        
        async def voiceCreateCallback(interaction: discord.Interaction):
            print("[MortyUI] VoiceCreate Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.VOICECREATE_CHANNEL.value)
            await interaction.response.edit_message(content="Please select a channel",view=view)
        
        async def voiceStorageCallback(interaction: discord.Interaction):
            print("[MortyUI] VoiceStorage Channel Button Clicked")
            view = UpdateChannelConfigView(self.sql,self.guild,utils.ChannelNames.VOICESTORAGE_CHANNEL.value)
            await interaction.response.edit_message(content="Please select a channel",view=view)

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
        voiceCreate.callback = voiceCreateCallback
        voiceStorage.callback = voiceStorageCallback

        doneButton.callback = doneCallback
        resetButton.callback = resetCallback

        self.add_item(core)
        self.add_item(smartDamage)
        self.add_item(voiceCreate)
        self.add_item(voiceStorage)

        self.add_item(doneButton)
        self.add_item(resetButton)

    async def on_timeout(self):
        try:
            await self.message.edit(view=None)
        except discord.NotFound:
            pass
            

#UpdateChannelConfig View
class UpdateChannelConfigView(discord.ui.View):

    def __init__(self, sql, guild,channel):
        super().__init__(timeout=None)
        self.sql = sql
        self.guild = guild
        self.channel = channel
        self.add_selector()
        self.add_buttons()

    def add_selector(self):

        selector = discord.ui.ChannelSelect(placeholder="Select a channel", min_values=1, max_values=1,row=0)
        selector.channel_types = [discord.ChannelType.text]
        
        

        async def selectorCallback(interaction: discord.Interaction):
            print(f"[MortyUI] Selector Choice: {selector.values[0].id} ({selector.values[0]})")

            #save the channel to the database
            res = utils.saveChannel(self.sql, self.guild.id,self.channel ,selector.values[0].id)
            if(res):
                view = SetupView(self.sql,self.guild)
                await interaction.response.edit_message(content=f"Successfully updated, any other changes?",view=view)
        selector.callback = selectorCallback
        self.add_item(selector)

    def add_buttons(self):
        
        cancel = discord.ui.Button(label='Cancel', style=discord.ButtonStyle.red, row=1)

        async def cancelCallback(interaction: discord.Interaction):
            print("Cancel Button Clicked")
            view = SetupView(self.sql,self.guild)
            await interaction.response.edit_message(content="Choose an option to configure:",view=view)
    
        cancel.callback = cancelCallback
        self.add_item(cancel)
    