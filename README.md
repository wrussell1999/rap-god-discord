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

Follow [this guide](https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python) to get GCP text-to-speech working. Put the JSON file in the config folder and name it ```google_cloud_key.json```.

#### Discord credentials

Follow [this guide](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) to get a Discord bot setup on your server.

`config/discord.json`

```json
{
    "token": "<bot token goes here>",
    "voice_channel_id": 1234
}
```

### Requirements

Requires ffmpeg (may not actually require it anymore) installed separately for audio. All python libraries are installed with:
```bash
pip3 install -r requirements.txt
```

Then following python need to be run to get the natural language data sets:
```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
```

## Contributors

- [Will Russell](https://github.com/wrussell1999): Discord bot, text to speech with GCP, and mp3 layering.
- [Justin Chadwell](https://github.com/jedevc): Natural language processing and lyric generation.
