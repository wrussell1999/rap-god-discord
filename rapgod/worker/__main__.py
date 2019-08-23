import time

if __name__ == "__main__":
    from . import WorkerPool

    pool = WorkerPool(thread_count=4)

    pool.start()

    for i in range(5):
        pool.enqueue("test",i)

    # time.sleep(20)
    # results = pool.results()
    # print(len(results))

    print("Wait for end")
    # while pool.busy():
    #     time.sleep(1)

    pool.join()

    results = pool.results()
    print(len(results))
