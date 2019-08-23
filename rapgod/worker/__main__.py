import time

if __name__ == "__main__":
    from . import ContainedPool

    pool = ContainedPool(thread_count=4)
    pool.start()
    time.sleep(5)

    for i in range(50):
        pool.enqueue("test",1)

    time.sleep(10)
