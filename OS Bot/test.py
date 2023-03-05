import discord, asyncio, youtube_dl, requests, openai
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands


# quality and format settings for audio conversion using FFMpeg
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents = discord.Intents.all())
voice_client = None
pause = False
queue = asyncio.Queue()
queue_list = []
# API ninja key, not used for playing music
ninjaAPI_key = "PaCYGLeW8RrD2HYFQNy50g==1oBSGfM4b0PuF58R"
openai.api_key = "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"



def get_fact():
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
        
async def play_song(message):
    global queue, queue_list, voice_client
    if voice_client is None:
        author = message.author
        voice_channel = author.voice.channel
        voice_client = await voice_channel.connect()
    queue_list.append(message.content.split()[1])
    if voice_client.is_playing() is False:
        await play_next_song(voice_client)

async def play_next_song(vc):
    global queue_list
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        url = queue_list[0]
        info = ydl.extract_info(url, download=False)
        player = vc.play(discord.FFmpegOpusAudio(info['url']), after=lambda e: print('Player error: %s' % e) if e else play_next_song(vc))

@bot.event
async def on_ready():   
    print('Bot is ready.')

###############################################################
class Menu(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.value = None	
	
	@discord.ui.button(label='Send Message', style=discord.ButtonStyle.blurple)
	async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction):
	    await interaction.response.send_message("Hello You Clicked ME")
	
@bot.command()
async def menu(ctx):
	view = Menu()
	await ctx.reply(view=view)


############################################################

@bot.event
async def on_message(message):
    global voice_client, queue_list, pause, queue
    if message.content.startswith('!play'):
        await play_song(message)
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
        await message.channel.send("Songs in the queue:\n")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            for i in queue_list:
                info = ydl.extract_info(i, download=False)
                title = info.get('title', None)
                information = ("Song Information: {title}\n").format(title=title) 
                await message.channel.send(information)  
    if message.content == "!fact":
        await message.channel.send(get_fact())
    if message.content.startswith("!rhyme"):
        await message.channel.send(get_rhyme(message.content.split()[1]))
    if message.content == "!help":
        help_answer = "Hey {}, the commands are as follows:\n 1. !play (song) \n 2. !pause \n 3. !fact \n 4. !rhyme (word) ".format(message.author.name)
        await message.channel.send(help_answer)
    if message.content.startswith("!dalle"):
        if get_moderation(message.content.split()[1]) == False:
            await message.channel.send(get_image(message.content[7:]))
        else:
            scolding = "Naughty boy {}. Image will not be processed. Try a different prompt. ".format(message.author.name)
            await message.channel.send(scolding)  
    if message.content.startswith("!gpt"):
        await message.channel.send(get_gpt(message.content[5:]))
    await bot.process_commands(message)



bot.run('MTA3MzEwMDA5MzUzNzkxMDgxNA.GQbbyi.yKlRgXlxd52WgYy5WrLUC71NmJQtXWauEXrTDQ')





