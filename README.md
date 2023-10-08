# Discord Bot with Various Features

This is a Python Discord bot with various features, including playing music from YouTube, providing interesting facts, generating rhymes, using the GPT-3.5 model for text generation, and more.

## Prerequisites

Before running the bot, make sure you have the following installed:

- Python 3.x
- Discord.py
- requests
- openai
- configparser
- youtube-dl (yt_dlp)
- youtubesearchpython

You'll also need to set up a Discord bot and obtain API keys for the OpenAI GPT-3.5 model and Ninja API. Configure these keys in `config.ini` before running the bot.

## Features

### Music

- Play music from YouTube using `!play (song)` or `!play (search query)`.
- Pause and resume playback with `!pause` and `!resume`.
- Skip the current song with `!skip`.
- View the queue with `!queue`.

### Fun and Information

- Get interesting facts with `!fact`.
- Generate rhymes for a word with `!rhyme (word)`.
- Use the GPT-3.5 model for text generation with `!gpt (prompt)` and `!dalle (prompt)`.
- Get more generated text based on the previous fact with `!more`.

### Help

- View the list of available commands with `!help`.

### Search

- Search for videos on YouTube with `!search (query)`.

## Usage

1. Run the bot by executing the script.
2. Invite the bot to your Discord server.
3. Use the provided commands to interact with the bot.

**Note**: Ensure the bot has proper permissions to join voice channels and send messages in your server.

## Author

This Discord bot was created by [Author Name].

## License

This project is licensed under the [License Name] License - see the [LICENSE](LICENSE) file for details.
