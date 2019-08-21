import os
from google.cloud import texttospeech
from pydub import AudioSegment
from io import BytesIO
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('config/google_cloud_key.json')
client = texttospeech.TextToSpeechClient(credentials=credentials)

# pre load backing track
backing_track = AudioSegment.from_mp3('static/audio/beat.mp3')

def make_stream(text):
    global backing_track
    print('↳ Running speech synthesis...')
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=0.93,
        pitch=-6.0)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    print('↳ Processing result...')
    voice_buffer = BytesIO(response.audio_content)
    voice_track = AudioSegment.from_mp3(voice_buffer)
    voice_track = voice_track.set_frame_rate(96000)

    print('↳ Mixing tracks...')
    output_track = voice_track.overlay(backing_track, position=100)
    output_track = output_track.set_frame_rate(48000)

    print('↳ Re-encoding...')
    raw_pcm_buffer = BytesIO()
    output_track.export(raw_pcm_buffer, format='s16le')
    raw_pcm_buffer.seek(0)

    return raw_pcm_buffer
