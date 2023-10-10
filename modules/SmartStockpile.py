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


async def makeStockpileEmbeds(stockpiles: List[Stockpile], interaction: discord.Interaction):
    await interaction.response.send_message("Generating embeds...", ephemeral=True)

    

    stockpiles_by_hex = defaultdict(list)
    for pile in stockpiles:
        stockpiles_by_hex[pile.hexid].append(pile)

    for hex, piles in stockpiles_by_hex.items():
        embed, edit_buttons = createHexEmbed(piles)

        view = StockpileEditButtons(buttons=edit_buttons)

        await interaction.channel.send(embed=embed,view=view)
    
    return "Embeds sent!"



def createHexEmbed(piles: List[Stockpile]) -> discord.Embed:
    first_pile = piles[0]
    embed = discord.Embed(title=utils.padEmbed(f"Stockpiles in {first_pile.hexname}"))  # Added padding back
    
    #Button objects
    linked_buttons = []
    
    #Button index
    

    index = 0
    towns = set(pile.townname for pile in piles)
    linked_buttons.clear()
    
    # pileIndex=0
    # for town in towns:
    #     for pile in piles:
    #         new = utils.linkedStockpile(index=pileIndex, stockpile_id=pile.stockpileid, button_label=label)
    #         linked_buttons.append(new)
    #         pileIndex += 1
    
    pileIndex = 0
    for town in towns:
        town_piles = []
        button_index = []
        
        for pile in piles:
            
            if pile.townname == town:
                label=f"L{pileIndex}"
                new = utils.linkedStockpile(index=index, stockpile_id=pile.stockpileid, button_label=label)
                linked_buttons.append(new)
                button_index.append(index)
                index += 1
                town_piles.append(pile)
                pileIndex += 1
        
        addTownToEmbed(town_piles, embed, button_index, linked_buttons)

    embed.set_thumbnail(url="https://static.wikia.nocookie.net/foxhole_gamepedia_en/images/d/d7/Map_Endless_Shore.png/revision/latest/scale-to-width-down/1000?cb=20220924114234")
    
    
    return embed, linked_buttons



def addTownToEmbed(town_piles: List[Stockpile], embed: discord.Embed, button_index: list, linked_buttons: List[utils.linkedStockpile]):
    edit_buttons = []
    
    town_name = town_piles[0].townname
    
    #for each location add an entry to edit_buttons array
    for index,(pile) in enumerate(town_piles):
        #edit_buttons.append(index)
        pass
    
    locations = []
    for index, pile in enumerate(town_piles):
        # Append the index and stockpile name to the locations list
        location_with_index = f"{linked_buttons[index].button_label}: {pile.stockpilename}"
        locations.append(location_with_index)
        edit_buttons.append(linked_buttons[index])
        button_index.pop(0)

    locations = '\n'.join(locations)
    
    #locations = '\n'.join(pile.stockpilename for pile in town_piles)
    codes = '\n'.join(str(pile.code) for pile in town_piles)
    expires = '\n'.join(utils.discordTimestamp(pile.expires) for pile in town_piles)

    embed.add_field(name=town_name, value=locations, inline=True)
    embed.add_field(name="Code", value=codes, inline=True)
    embed.add_field(name="Expires", value=expires, inline=True)

    return edit_buttons

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