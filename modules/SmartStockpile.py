import discord
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict

# Consider creating a utils.py file for utility functions like discordTimestamp
import modules.utils as utils  

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
        embed = createHexEmbed(piles)
        await interaction.channel.send(embed=embed)
    
    return "Embeds sent!"


def createHexEmbed(piles: List[Stockpile]) -> discord.Embed:
    first_pile = piles[0]
    embed = discord.Embed(title=utils.padEmbed(f"Stockpiles in {first_pile.hexname}"))  # Added padding back

    towns = set(pile.townname for pile in piles)
    for town in towns:
        town_piles = [pile for pile in piles if pile.townname == town]
        addTownToEmbed(town_piles, embed)

    embed.set_thumbnail(url="https://static.wikia.nocookie.net/foxhole_gamepedia_en/images/d/d7/Map_Endless_Shore.png/revision/latest/scale-to-width-down/1000?cb=20220924114234")
    return embed



def addTownToEmbed(town_piles: List[Stockpile], embed: discord.Embed):
    town_name = town_piles[0].townname
    
    locations = '\n'.join(pile.stockpilename for pile in town_piles)
    codes = '\n'.join(str(pile.code) for pile in town_piles)
    expires = '\n'.join(utils.discordTimestamp(pile.expires) for pile in town_piles)

    embed.add_field(name=town_name, value=locations, inline=True)
    embed.add_field(name="Code", value=codes, inline=True)
    embed.add_field(name="Expires", value=expires, inline=True)
