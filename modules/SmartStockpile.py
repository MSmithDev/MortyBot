import discord
from dataclasses import dataclass
from typing import List
from collections import defaultdict

@dataclass
class Stockpile:
    guild: int
    townid: int
    townname: str
    stockpileid: int
    location: str
    expires: int
    created: str
    last: str


async def getGuildStockpiles(sql, guild):

    #Build the query based on the parameters given
    query = f"""
    SELECT stockpiles.townid, towns.name, stockpiles.stockpileid, stockpiles.location,
    stockpiles.expires, stockpiles.createdby, stockpiles.lastperson
    FROM stockpiles INNER JOIN towns ON stockpiles.townid=towns.townid
    WHERE stockpiles.guild={guild}
    """

    #execute the query
    cursor = await sql.execute(query)

    #Get the results
    rows = await cursor.fetchall()

    #List of stockpiles
    stockpiles: List[Stockpile] = []
    
    #Loop through the results and create a stockpile object for each
    for row in rows:
        stockpiles.append(Stockpile(guild,row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

    return stockpiles

async def makeStockpileEmbeds(stockpile: List[Stockpile], channel):

    stockpiles_by_town = defaultdict(list)
    for pile in stockpile:
        stockpiles_by_town[pile.townid].append(pile)

    for townid, town_stockpiles in stockpiles_by_town.items():
        embed = discord.Embed(title=f"Stockpiles in {town_stockpiles[0].townname}")

        # Prepare the values for each field
        locations = '\n'.join([pile.location for pile in town_stockpiles])
        codes = '\n'.join([str(pile.stockpileid) for pile in town_stockpiles])
        expires = '\n'.join([str(pile.expires) for pile in town_stockpiles])  # You might need to format this differently

        embed.add_field(name="Location", value=locations)
        embed.add_field(name="Code", value=codes)
        embed.add_field(name="Expires", value=expires)

        await channel.send(embed=embed)
    return "todo"

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
    