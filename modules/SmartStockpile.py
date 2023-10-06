import discord
from dataclasses import dataclass
from typing import List
from collections import defaultdict
import modules.utils as utils
@dataclass
class Stockpile:
    guild: int
    townid: int
    townname: str
    stockpileid: int
    location: str
    code: int
    expires: int
    created: str
    last: str


async def getGuildStockpiles(sql, guild):

    #Build the query based on the parameters given
    query = f"""
    SELECT stockpiles.townid, towns.name, stockpiles.stockpileid, stockpiles.location, stockpiles.code,
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
        stockpiles.append(Stockpile(guild,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

    return stockpiles

async def makeStockpileEmbeds(stockpile: List[Stockpile], interaction: discord.Interaction):
    await interaction.response.send_message("Testing", ephemeral=True)
    stockpiles_by_town = defaultdict(list)
    for pile in stockpile:
        stockpiles_by_town[pile.townid].append(pile)

    for townid, town_stockpiles in stockpiles_by_town.items():
        title = f"Stockpiles in {town_stockpiles[0].townname}"
        print("[SmartStockpile] Title before: " + str(len(title)))
        print("[SmartStockpile] Title after: " + str(len(utils.padEmbed(title))))
        embed = discord.Embed(title=utils.padEmbed(title))

        # Prepare the values for each field
        locations = '\n'.join([pile.location for pile in town_stockpiles])
        codes = '\n'.join([str(pile.code) for pile in town_stockpiles])
        expires = '\n'.join([utils.discordTimestamp(pile.expires) for pile in town_stockpiles])  # You might need to format this differently

        embed.add_field(name="Location", value=locations)
        embed.add_field(name="Code", value=codes)
        embed.add_field(name="Expires", value=expires)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/foxhole_gamepedia_en/images/d/d7/Map_Endless_Shore.png/revision/latest/scale-to-width-down/1000?cb=20220924114234")
        await interaction.channel.send(embed=embed)
    return "todo"


    