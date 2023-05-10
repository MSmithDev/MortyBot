# BotGPT

GPT Powered Discord Bot

## Requirements
Python 3.8 or higher <br>
OpenAI API Key <br>
ElevenLabs API Key (optional for realistic voice)

## Dependancies
Discord with voice:
```bash
pip install -U discord.py[voice]
```
OpenAI:
```bash
pip install openai
pip install tiktoken
```
ElevenLabsLib:
```bash
pip install elevenlabslib
```

## Setup
In the root directory create a .env file, add the following lines and replace the values with your own. If you don't have an ElevenLabs API key, you must remove the line. The BOT_ID is your bots discord id, you can find this with developer tools enabled then right click your bot and click "Copy User ID". 

```
DISCORD_TOKEN=your-bot-token
BOT_ID=@<bot-id-number>
OPENAI_API_KEY=your-api-key
ELEVENLABS_API_KEY=your-api-key
```
