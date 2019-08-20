import os
from google.cloud import texttospeech
from pydub import AudioSegment
from io import BytesIO
from google.oauth2 import service_account

import time

credentials = service_account.Credentials.from_service_account_file('config/google_cloud_key.json')
client = texttospeech.TextToSpeechClient(credentials=credentials)


def make_stream(text):
    print('Running speech synthesis...', end='', flush=True)
    PERF_start = time.time()

    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.OGG_OPUS,
        speaking_rate=0.93,
        pitch=-6.0)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    PERF_end = time.time()
    print(f' [{PERF_end - PERF_start}]')
    print('Processing result...', end='', flush=True)
    PERF_start = time.time()

    voice_buffer = BytesIO(response.audio_content)
    voice_track = AudioSegment.from_ogg(voice_buffer)
    voice_track = voice_track.set_frame_rate(96000)

    PERF_end = time.time()
    print(f' [{PERF_end - PERF_start}]')
    print('Loading backing track...', end='', flush=True)
    PERF_start = time.time()

    backing_track = AudioSegment.from_ogg('static/audio/beat.ogg')

    PERF_end = time.time()
    print(f' [{PERF_end - PERF_start}]')
    print('Mixing tracks...', end='', flush=True)
    PERF_start = time.time()

    output_track = voice_track.overlay(backing_track, position=100)
    output_track = output_track.set_frame_rate(48000)

    PERF_end = time.time()
    print(f' [{PERF_end - PERF_start}]')
    print('Re-encoding...', end='', flush=True)
    PERF_start = time.time()

    raw_pcm_buffer = BytesIO()
    output_track.export(raw_pcm_buffer, format='s16le')
    raw_pcm_buffer.seek(0)

    PERF_end = time.time()
    print(f' [{PERF_end - PERF_start}]')
    return raw_pcm_buffer
