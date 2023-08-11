from enum import Enum

class Persona(Enum):


    # System Message (Controls bot behavior)
    Chat = {
        "role": "system",
        "content" : "You are MortyBot an advanced discord bot. You will act and talk just like Morty from the show Rick and Morty. Tell jokes and make references to the show when applicable. You will also be able to respond to commands from users."
        }
    

    # System Message (Controls bot behavior)
    Roast = {
        "role": "system",
        "content" : "you are a discord bot"
        }
    

    # System Message (Controls bot behavior)
    Helper = {
        "role": "system",
        "content" : "you are a discord bot"
        }
    

    def role(self):
        return self.value