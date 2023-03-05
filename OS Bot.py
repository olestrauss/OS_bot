import discord, asyncio, requests, openai, configparser
import yt_dlp as youtube_dl
from youtubesearchpython import VideosSearch

# quality and format settings for audio conversion using FFMpeg
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

config = configparser.ConfigParser()
config.read('config.ini')
print(config.get("discord_token", "key"))
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
voice_client = None
pause = False
queue = asyncio.Queue()
queue_list = []
# API ninja key, not used for playing music
ninjaAPI_key = str(config.get('ninjaAPI', 'key'))
openai.api_key = str(config.get('OpenAPI', 'key'))
bot_key = str(config.get('discord_token', 'key'))



def get_fact():
    global fact
    api_url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(1)
    fact = requests.get(api_url, headers={'X-Api-Key': ninjaAPI_key})
    fact = fact.text.replace('[{"fact": "', "")
    return fact.replace('"}]', ".")

def get_rhyme(word):
    api_url = 'https://api.api-ninjas.com/v1/rhyme?word={}'.format(word)
    rhymingword = requests.get(api_url, headers={'X-Api-Key': ninjaAPI_key})
    return rhymingword.text

def get_moderation(text):
    check = '"has_profanity": true'
    api_url = 'https://api.api-ninjas.com/v1/profanityfilter?text={}'.format(text)
    response = requests.get(api_url, headers={'X-Api-Key': ninjaAPI_key})
    if check in response.text:
        return True
    else:
        return False

def get_image(prompt):
    global openai_key, openai_url 
    response = openai.Image.create(
    prompt = prompt,
    n=1,
    size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url   

def get_gpt(prompt):
    global openai_key
    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=0.5)
    return response["choices"][0]["text"]

def get_search(word_to_search):
    global urls_of_search
    videosSearch = VideosSearch(word_to_search, limit = 4)
    results = videosSearch.result()["result"]
    titles_of_search, urls_of_search = [], []
    for item in results:
        title = item["title"]
        url = item["link"]
        titles_of_search.append(title)
        urls_of_search.append(url)
    return titles_of_search

async def play_song(message, digit = False):
    global queue, queue_list, voice_client
    if not digit:
        if voice_client is None:
            author = message.author
            voice_channel = author.voice.channel
            voice_client = await voice_channel.connect()
        queue_list.append(message.content.split()[1])
        if voice_client.is_playing() is False:
            await play_next_song(voice_client)
    elif digit:
        if voice_client is None:
            author = message.author
            voice_channel = author.voice.channel
            voice_client = await voice_channel.connect()
        queue_list.append(urls_of_search[int(message.content[6:])-1])
        if voice_client.is_playing() is False:
            await play_next_song(voice_client)


async def play_next_song(vc):
    global queue_list
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        url = queue_list[0]
        info = ydl.extract_info(url, download=False)
        player = vc.play(discord.FFmpegOpusAudio(info['url']), after=lambda e: print('Player error: %s' % e) if e else play_next_song(vc))    

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    global voice_client, queue_list, pause, queue, fact, urls
    if message.content.startswith('!play'):
            if message.author.voice:
                if not message.content[6:].isdigit():
                    await play_song(message)
                elif message.content[6:].isdigit():
                    await play_song(message, True)
            else:
                await message.channel.send("Please connect to a voice channel first!")
    if message.content == "!pause":
        if pause == False:
            voice_client.pause()
            pause = True
        elif pause == True:
            voice_client.resume()
            pause = False
    if message.content == "!skip":
        voice_client.stop()
        queue_list.pop(0)
        await play_next_song(voice_client)
    if message.content == "!queue":
        if queue_list:    
            await message.channel.send("Songs in the queue:\n")
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                for i in queue_list:
                    info = ydl.extract_info(i, download=False)
                    title = info.get('title', None)
                    information = ("{title}\n").format(title=title)
                    await message.channel.send(information)
        else:
            await message.channel.send("The queue is empty. To play a song, type !play followed by the URL")
    if message.content == "!fact":
        await message.channel.send(get_fact())
    if message.content.startswith("!rhyme"):
        await message.channel.send(get_rhyme(message.content.split()[1]))
    if message.content == "!help":
        help_answer = "Hey {}, the commands are as follows:\n 1. !play (song) \n 2. !pause \n 3. !fact \n 4. !rhyme (word) \n 5. !gpt (prompt) \n 6. !dalle (prompt) \n 7. !more \n 8. !skip ".format(message.author.name)
        await message.channel.send(help_answer)
    if message.content.startswith("!dalle"):
        if get_moderation(message.content.split()[1]) == False:
            await message.channel.send(get_image(message.content[7:]))
        else:
            scolding = "Naughty boy {}. Image will not be processed. Try a different prompt. ".format(message.author.name)
            await message.channel.send(scolding)
    if message.content.startswith("!gpt"):
        await message.channel.send(get_gpt(message.content[5:]))
    if message.content.startswith("!more"):
        await message.channel.send(get_gpt(fact))
    if message.content.startswith("!search"):
        for i, e in enumerate(get_search(message.content[8:])):
            await message.channel.send(f"{i+1}. {e}")
        



client.run(bot_key)





