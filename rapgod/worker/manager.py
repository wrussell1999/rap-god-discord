import time
import queue
from threading import Thread, Event

from .. import lyrics
from .. import audio

from .worker import Worker

class WorkerPool:
    def __init__(self, thread_count=1):
        print(f'Worker pool created with {thread_count} thread(s)')
        # maxsize=0 means unlimited size
        self.work_queue = queue.Queue(maxsize=0)
        self.results_queue = queue.Queue(maxsize=0)
        self.thread_count = thread_count
        self.aborts = []
        self.threads = []
        self.idles = []
        self.backing_tracks = audio.load_backing_tracks()

    def start(self, block=False):
        if self.alive():
            return False

        print('Worker pool starting...')
        self.aborts = []
        self.idles = []
        self.threads = []
        for n in range(self.thread_count):
            abort = Event()
            idle = Event()
            self.aborts.append(abort)
            self.idles.append(idle)
            worker = Worker(f'thread-{n}',
                            self.work_queue,
                            self.results_queue,
                            abort,
                            idle,
                            self.backing_tracks)
            self.threads.append(worker)
        return True

    def enqueue(self, word, id):
        self.work_queue.put((word, id))

    def join(self):
        self.work_queue.join()

    def stop(self, block=False):
        for a in self.aborts:
            a.set()

        while block and self.alive():
            time.sleep(1)

    def alive(self):
        return True in [t.is_alive() for t in self.threads]

    def busy(self):
        return False in [i.is_set() for i in self.idles]

    def get_results(self):
        results = []
        try:
            while True:
                results.append(self.results_queue.get(block=False))
                self.results_queue.task_done()
        except queue.Empty:
            pass
        return results

    def get_result(self):
        try:
            result = self.results_queue.get(block=False)
            self.results_queue.task_done()
        except queue.Empty:
            return None
        return result
