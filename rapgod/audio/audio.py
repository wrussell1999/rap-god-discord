import random
from io import BytesIO
from pydub import AudioSegment
from pydub import effects
from google.cloud import texttospeech
from google.oauth2 import service_account

TRACK_NAMES = [
    'generic',
    'desiigner_panda',
    'eminem_not_alike',
    'eminem_type_beat',
    'future_mask_off',
    'lil_pump_type_beat',
    'lil_pump_type_beat2'
    ]

def init():
    global tts_client
    credentials = service_account.Credentials.from_service_account_file('config/google_cloud_key.json')
    tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

def load_backing_tracks():
    backing_tracks = []
    print("Loading backing tracks...")
    for name in TRACK_NAMES:
        print(f'↳ Load & normalize \'{name}\'')
        track = AudioSegment.from_mp3(f'static/audio/{name}.mp3')
        track = effects.normalize(track, headroom=6)
        backing_tracks.append(track)
    print("Done")

    return tuple(backing_tracks)

def make_stream(text, backing_track):
    # Running speech synthesis...
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=0.93,
        pitch=-6.0)

    response = tts_client.synthesize_speech(synthesis_input, voice, audio_config)

    # Processing result...
    voice_buffer = BytesIO(response.audio_content)
    voice_track = AudioSegment.from_mp3(voice_buffer)
    voice_track = voice_track.set_frame_rate(96000)

    # Mixing tracks...
    output_track = backing_track.overlay(voice_track, position=15000)
    output_track = output_track.set_frame_rate(48000)

    # Re-encoding...
    raw_pcm_buffer = BytesIO()
    output_track.export(raw_pcm_buffer, format='s16le')
    raw_pcm_buffer.seek(0)

    return raw_pcm_buffer

def save_stream(stream, path):
    track = AudioSegment.from_raw(
        stream,
        sample_width=2,
        frame_rate=48000,
        channels=2
    )

    track.export(path+'.mp3', format='mp3')
