import discord, asyncio, requests, openai, configparser, os, yt_dlp as youtube_dl
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
intents = discord.Intents.all()
client = discord.Client(intents=intents)
voice_client, pause, queue, queue_list = None, False, asyncio.Queue(), []
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
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}])
    return (response.choices[0].message["content"])

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
            await play_next_song(voice_client, message)
    elif digit:
        if voice_client is None:
            author = message.author
            voice_channel = author.voice.channel
            voice_client = await voice_channel.connect()
        queue_list.append(urls_of_search[int(message.content[6:])-1])
        if voice_client.is_playing() is False:
            await play_next_song(voice_client, message)

async def play_next_song(vc, message):
    global queue_list
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        url = queue_list[0]
        queue_list.pop(0)
        info = ydl.extract_info(url, download=False)
        player = vc.play(discord.FFmpegOpusAudio(info['url']), after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(voice_client, message), client.loop)) 
        await message.channel.send(f"Now playing {info.get('title', None)}")

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    global voice_client, queue_list, pause, queue, fact
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
        await play_next_song(voice_client, message)
    if message.content == "!queue":
        if queue_list:
            que = "Songs in the queue:\n"
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                for i, e in enumerate(queue_list):
                    info = ydl.extract_info(e, download=False)
                    title = info.get('title', None)
                    que += f"{i+1}. {title}\n"
                await message.channel.send(que)
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
        sear = ""
        for i, e in enumerate(get_search(message.content[8:])):
            sear += f"{i+1}. {e}\n"
        await message.channel.send(sear)
        



client.run(bot_key)





