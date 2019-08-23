import time
import queue
from threading import Thread
from multiprocessing import Process, Queue, Event

from .. import lyrics
from .. import audio

from .worker import Worker

class ContainedPool:
    def __init__(self, thread_count=1):
        print('Container process for worker pool created')
        self.work_queue = Queue(maxsize=0)
        self.results_queue = Queue(maxsize=0)
        self.thread_count = thread_count
        self.abort = Event()

    def start(self):
        print('Container process starting...')
        params = (self.work_queue, self.results_queue, self.thread_count, self.abort)
        self.process = Process(target=self._run_thread_pool, args=(params))
        self.process.start()

    def enqueue(self, word, id):
        self.work_queue.put((word, id))

    def join(self):
        self.work_queue.join()

    def get_result(self):
        try:
            result = self.results_queue.get(block=False)
        except queue.Empty:
            return None
        return result

    # def stop(self, block=False):
    #     print('Stopping container process...')
    #     self.abort.set()
    #
    #     if block:
    #         self.process.join()

    def _run_thread_pool(self, work_queue, results_queue, thread_count, abort):
        pool = ThreadPool(work_queue,
                               results_queue,
                               thread_count=thread_count
                              )

        pool.start()

        while not abort.is_set():
            time.sleep(1)

        print('Stopping contained pool...')
        pool.stop(block=True)

class ThreadPool:
    def __init__(self, work_queue, results_queue, thread_count=1):
        print(f'Worker pool created with {thread_count} thread(s)')
        # maxsize=0 means unlimited size
        self.work_queue = work_queue
        self.results_queue = results_queue
        self.thread_count = thread_count
        self.aborts = []
        self.threads = []
        self.idles = []
        self.backing_tracks = audio.load_backing_tracks()

    def start(self):
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
                            self.backing_tracks
                            )
            self.threads.append(worker)
        return True

    def enqueue(self, word, id):
        self.work_queue.put((word, id))

    # def stop(self):
    #     print('Worker pool stopping...')
    #     for a in self.aborts:
    #         a.set()
    #
    #     while self.alive():
    #         time.sleep(1)
    #
    #     print('Worker pool stopped')

    def alive(self):
        return True in [t.is_alive() for t in self.threads]
