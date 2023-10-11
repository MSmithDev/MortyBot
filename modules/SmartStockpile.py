import discord
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict
import modules.utils as utils  

#Views
from modules.MortyUI import StockpileEditButtons

#setup logging
import logging
logger = logging.getLogger("mortybot")



@dataclass
class Stockpile:
    guild: int
    hexid: int
    hexname: str
    townname: str
    stockpileid: int
    townid: int
    stockpilename: str
    code: int
    expires: int
    created: str
    lastperson: str


async def getGuildStockpiles(sql, guild):
    query = f"""
        SELECT 
            sp.hexid, h.name AS hex_name, t.name AS town_name, sp.stockpileid, 
            sp.townid, sp.name AS stockpile_name, sp.code, sp.expires, 
            sp.createdby, sp.lastperson
        FROM 
            stockpiles sp
        INNER JOIN hexs h ON sp.hexid=h.hexid
        INNER JOIN towns t ON sp.townid=t.townid 
        WHERE 
            sp.guild={guild}
    """
    
    cursor = await sql.execute(query)
    rows = await cursor.fetchall()
    
    return [Stockpile(guild, *row) for row in rows]



# Import necessary libraries
import discord
from typing import List
from collections import defaultdict
import modules.utils as utils
from modules.MortyUI import StockpileEditButtons

#setup logging
import logging
logger = logging.getLogger("mortybot")


async def makeStockpileEmbeds(stockpiles: List[Stockpile], interaction: discord.Interaction):
    await interaction.response.send_message("Generating embeds...", ephemeral=True)

    # Create a dictionary to map hexes to towns and stockpiles
    hex_town_map = defaultdict(lambda: defaultdict(list))
    for pile in stockpiles:
        hex_town_map[pile.hexid][pile.townname].append(pile)

    # Loop through each hex in the dictionary
    for hex in hex_town_map.items():
        pileIndex = 0
        linkedButtons = []

        # Create a new embed
        embed = discord.Embed()
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/foxhole_gamepedia_en/images/d/d7/Map_Endless_Shore.png/revision/latest/scale-to-width-down/1000?cb=20220924114234")

        # Loop through each town in the hex
        for town in hex[1]:

            # Set the title of the embed to the hex name
            embed.title = utils.padEmbed(f"Stockpiles in {hex[1][town][0].hexname}")

            locations = ""
            codes = ""
            expires = ""

            # Loop through each stockpile in the town
            for pile in hex[1][town]:
                # Add the stockpile information to the embed
                locations += f"L{pileIndex}: {pile.stockpilename}\n"
                codes += f"{pile.code}\n"
                expires += f"{utils.discordTimestamp(pile.expires)}\n"

                # Create a linked button for the stockpile
                new = utils.linkedStockpile(index=pileIndex, stockpile_id=pile.stockpileid, button_label=f"L{pileIndex}")
                linkedButtons.append(new)
                pileIndex += 1

            # Add the stockpile information to the embed
            embed.add_field(name=town, value=locations, inline=True)
            embed.add_field(name="Code", value=codes, inline=True)
            embed.add_field(name="Expires", value=expires, inline=True)

        # Create a view with the linked buttons
        view = StockpileEditButtons(buttons=linkedButtons)

        # Send the embed with the view
        await interaction.channel.send(embed=embed, view=view)

    return "Embeds sent!"


async def addGuildStockpile(sql, guild, stockpile: Stockpile):

    last_person_value = f'"{stockpile.lastperson}"' if stockpile.lastperson else "NULL"

    query = f"""
        INSERT INTO stockpiles 
            (hexid, guild, townid, name, code, expires, createdby, lastperson) 
        VALUES 
            ({stockpile.hexid}, {guild}, {stockpile.townid}, "{stockpile.stockpilename}", {stockpile.code}, {stockpile.expires}, "{stockpile.created}", {last_person_value})
    """

    logger.debug(f"[MortyBot] Adding stockpile to guild {guild}: {stockpile}")
    
    cursor = await sql.execute(query)
    await sql.commit()

    logger.debug(f"[MortyBot] Stockpile added to guild {guild}")

    #Todo: Re-render the embeds for the guild