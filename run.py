import asyncio
import discord

BOT_TOKEN = ''
THREAD_MESSAGE_FETCH_ATTEMPT_TIMEOUT = 1
MAX_THREAD_MESSAGE_FETCH_ATTEMPTS = 5

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    print(f'{client.user} is on {len(client.guilds)} server(s)')

@client.event
async def on_thread_create(thread):
    '''
    Pins first message in a thread
    '''
    # Workaround: first message is not defined right away
    # => Attempt fetching several times
    for _ in range(MAX_THREAD_MESSAGE_FETCH_ATTEMPTS):
        if thread.last_message_id is not None:
            break
        await asyncio.sleep(THREAD_MESSAGE_FETCH_ATTEMPT_TIMEOUT)
    else:
        return
    
    async for message in thread.history(oldest_first=True):
        await message.pin()
        break

@client.event
async def on_raw_reaction_add(reaction):
    '''
    Pins message if thread owner reacts to it with :pushpin:
    '''
    if reaction.emoji.name != '📌':
        return

    thread = await client.fetch_channel(reaction.channel_id)

    if not isinstance(thread, discord.Thread):
        return
    
    if reaction.user_id != thread.owner_id:
        return
    
    message = await thread.fetch_message(reaction.message_id)
    await message.pin()

@client.event
async def on_raw_reaction_remove(reaction):
    '''
    Unpins message if thread owner removes :pushpin: reaction
    '''
    if reaction.emoji.name != '📌':
        return

    thread = await client.fetch_channel(reaction.channel_id)

    if not isinstance(thread, discord.Thread):
        return
    
    if reaction.user_id != thread.owner_id:
        return
    
    message = await thread.fetch_message(reaction.message_id)
    await message.unpin()

@client.event
async def on_guild_join(guild):
    print(f'{client.user} joined {guild.name}')
    print(f'{client.user} is now on {len(client.guilds)} server(s)')

@client.event
async def on_guild_remove(guild):
    print(f'{client.user} left {guild.name}')
    print(f'{client.user} is now on {len(client.guilds)} server(s)')

client.run(BOT_TOKEN)
