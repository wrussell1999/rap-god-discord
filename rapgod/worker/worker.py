import time
import queue
import random
from threading import Thread
from multiprocessing import Queue

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
                word, id = self.work_queue.get(timeout=1)
                self.idle.clear()
            except queue.Empty:
                self.idle.set()
                continue

            try:
                stream = self.make_track(word, id)
                result = (stream, id)
                self.results_queue.put(result)
            except Exception as e:
                raise e
        print(f'{self.name}: Exiting')

    def make_track(self, theme_word, backing_track):
        start = time.time()
        print(f'{self.name}: Processing (theme \'{theme_word}\')...')

        # Generating lyrics
        rap_lyrics = self.generator.generate_lyrics(theme_word)

        # Generating audio...
        backing_track = random.choice(self.backing_tracks)
        stream = audio.make_stream(rap_lyrics, backing_track)

        end = time.time()
        print(f'{self.name}: Done [{end - start}s]')
        return stream
