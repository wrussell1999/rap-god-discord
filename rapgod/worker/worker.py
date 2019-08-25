import time
import queue
import random
from threading import Thread

from .. import lyrics
from .. import audio

class Worker(Thread):
    def __init__(self, name, queue, results, abort, idle, backing_tracks):
        Thread.__init__(self)
        self.name = name
        self.daemon = True

        audio.init()
        self.abort = abort
        self.idle = idle
        self.work_queue = queue
        self.results_queue = results
        self.generator = lyrics.Generator(lyrics.load_songs())
        self.backing_tracks = backing_tracks

        self.start()

    def run(self):
        print(f'{self.name}: Awake')
        while not self.abort.is_set():
            try:
                work = self.work_queue.get(timeout=1)
                self.do_work(work)
            except queue.Empty:
                self.idle.set()

        print(f'{self.name}: Exiting')

    def do_work(self, work):
        self.idle.clear()

        task_name, args = work
        if task_name == "make_track":
            word, id = args
            result = self.make_track(word)
        elif task_name == "encode_track":
            raw_stream, id = args
            result = self.encode_track(raw_stream)
        elif task_name == "make_and_encode":
            word, id = args
            pcm_stream = self.make_track(word)
            result = self.encode_track(pcm_stream)

        self.results_queue.put((task_name, result, id))

    def encode_track(self, stream):
        start = time.time()
        print(f'{self.name}: Converting stream...')

        mp3_stream = audio.mp3_encode_stream(stream)

        end = time.time()
        print(f'{self.name}: Done [{end - start}s]')
        return mp3_stream

    def make_track(self, theme_word):
        start = time.time()
        print(f'{self.name}: Making track (theme \'{theme_word}\')...')

        # Generating lyrics
        rap_lyrics = self.generator.generate_lyrics(theme_word)

        # Generating audio...
        backing_track = random.choice(self.backing_tracks)
        stream = audio.make_stream(rap_lyrics, backing_track)

        end = time.time()
        print(f'{self.name}: Done [{end - start}s]')
        return stream
