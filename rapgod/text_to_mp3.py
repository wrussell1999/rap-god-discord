import os
from google.cloud import texttospeech
from pydub import AudioSegment

client = texttospeech.TextToSpeechClient()


def make_mp3(text, filename):
    print("Starting sound synthesis...")
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=0.93,
        pitch=-6.0)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    with open(filename, 'w+b') as out:
        out.write(response.audio_content)
        print(f'Audio content written to {filename}')
    sound1 = AudioSegment.from_mp3(filename)
    sound2 = AudioSegment.from_mp3("static/audio/beat.mp3")
    output = sound1.overlay(sound2, position=100)

    new_filename = os.path.join(os.path.dirname(
        filename), 'mod-' + os.path.basename(filename))
    print(new_filename)
    output.export(new_filename, format="mp3")
    return new_filename
