# Rap God - Discord Edition

[Rap God](https://github.com/jedevc/royal-hackaway-2019) was a pretty cool hackathon project, built using the Nexmo API. I thought it would be cool to implement the same thing, but inside of Discord using voice channels...

## Usage

Type `!rap <word>` to start the rap process.

## Development

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip3 install -r requirements.txt
```

### Configuration

#### Google Cloud Platform credentials

Follow [this guide](https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python) to get GCP text-to-speech working

#### Discord credentials 

Follow [this guide](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) to get a Discord bot setup on your server.

`config/discord.json`

```json
{
    "token": "string",
    "voice_channel_id": 1234
}
```

### Requirements

Requires ffmpeg installed separately for audio. All python ones are installed with `requirements.txt`

## Contributors

- [Will Russell](https://github.com/wrussell1999): Discord bot, text to speech with GCP, and mp3 layering.
- [Justin Chadwell](https://github.com/jedevc): Natural language processing and lyric generation.
