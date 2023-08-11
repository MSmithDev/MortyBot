import logging
import discord

#setup logging
logger = logging.getLogger("mortybot")

functions = [
        {
            "name": "get_userid_in_voice",
            "description": "Get the user ID of a user in voice chat",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Name or alias of the user to get the ID of",
                    },
                },
            },
        },
        {
            "name": "disconnect_user_in_voice",
            "description": "Disconnect a user from voice chat by user ID, Use get_userid_in_voice to get the user ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "user ID": {
                        "type": "string",
                        "description": "The user ID to disconnect",
                    },
                },
            },
        }
    ]



async def get_userid_in_voice(username: str, interaction: discord.Interaction) -> str:
    if username is None:
        return None
    else:
        logger.debug(f"[GPTFunctions] get_userid_in_voice: {username}")

        guild = interaction.guild

        if guild:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if member.name.lower().startswith(username):
                        return member.id


        return "[Error] User not found"
    

async def disconnect_user_in_voice(user_id: str) -> str:
    if user_id is None:
        return "User ID is None"
    else:
        logger.debug(f"[GPTFunctions] disconnect_user_in_voice: {user_id}")
        return "success"