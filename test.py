import multiprocessing
import threading
import time
import matplotlib.pyplot as plt


# -------------------------------------------------
# MATRIX
# -------------------------------------------------

A = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

B = [
    [9, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
]

N = 3


# -------------------------------------------------
# SEQUENTIAL
# -------------------------------------------------

def sequential():

    C = [[0] * N for _ in range(N)]

    for i in range(N):

        time.sleep(1)       # Simulate heavy work

        for j in range(N):
            C[i][j] = A[i][j] + B[i][j]

    return C


start = time.perf_counter()

C1 = sequential()

seq_time = time.perf_counter() - start


# -------------------------------------------------
# POOL
# -------------------------------------------------

def add_row(data):

    row1, row2 = data

    time.sleep(1)           # Simulate heavy work

    return [x + y for x, y in zip(row1, row2)]


start = time.perf_counter()

with multiprocessing.Pool(3) as pool:

    C2 = pool.map(add_row, zip(A, B))

pool_time = time.perf_counter() - start


# -------------------------------------------------
# PROCESS
# -------------------------------------------------

def add_process(row, queue):

    time.sleep(1)           # Simulate heavy work

    result = []

    for j in range(N):
        result.append(A[row][j] + B[row][j])

    queue.put((row, result))


if __name__ == "__main__":

    C3 = [[0] * N for _ in range(N)]

    queue = multiprocessing.Queue()

    processes = []

    start = time.perf_counter()

    # Create 3 processes

    for i in range(N):

        p = multiprocessing.Process(
            target=add_process,
            args=(i, queue)
        )

        processes.append(p)

        p.start()


    # Receive results

    for i in range(N):

        row, result = queue.get()

        C3[row] = result


    # Wait for processes

    for p in processes:
        p.join()


    process_time = time.perf_counter() - start


    # -------------------------------------------------
    # MULTITHREADING
    # -------------------------------------------------

    C4 = [[0] * N for _ in range(N)]


    def add_thread(row):

        time.sleep(1)       # Simulate heavy work

        for j in range(N):

            C4[row][j] = A[row][j] + B[row][j]


    threads = []

    start = time.perf_counter()


    # Create 3 threads

    for i in range(N):

        t = threading.Thread(
            target=add_thread,
            args=(i,)
        )

        threads.append(t)

        t.start()


    # Wait for threads

    for t in threads:
        t.join()


    thread_time = time.perf_counter() - start


    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------

    print("\nMatrix A:")

    for row in A:
        print(row)


    print("\nMatrix B:")

    for row in B:
        print(row)


    print("\nResult using Sequential:")

    for row in C1:
        print(row)


    print("\nResult using Pool:")

    for row in C2:
        print(row)


    print("\nResult using Process:")

    for row in C3:
        print(row)


    print("\nResult using Threading:")

    for row in C4:
        print(row)


    # -------------------------------------------------
    # EXECUTION TIME
    # -------------------------------------------------

    print("\nExecution Time:")

    print("Sequential :", seq_time)
    print("Pool       :", pool_time)
    print("Process    :", process_time)
    print("Threading  :", thread_time)


    # -------------------------------------------------
    # SPEEDUP
    # -------------------------------------------------

    pool_speedup = seq_time / pool_time
    process_speedup = seq_time / process_time
    thread_speedup = seq_time / thread_time


    print("\nSpeedup:")

    print("Sequential :", 1)
    print("Pool       :", pool_speedup)
    print("Process    :", process_speedup)
    print("Threading  :", thread_speedup)


    # -------------------------------------------------
    # GRAPH
    # -------------------------------------------------

    methods = [
        "Sequential",
        "Pool",
        "Process",
        "Threading"
    ]


    execution_times = [
        seq_time,
        pool_time,
        process_time,
        thread_time
    ]


    speedups = [
        1,
        pool_speedup,
        process_speedup,
        thread_speedup
    ]


    # Execution Time Graph

    plt.figure(figsize=(8, 5))

    plt.bar(methods, execution_times)

    plt.xlabel("Technique")
    plt.ylabel("Execution Time (seconds)")

    plt.title("Execution Time Comparison")

    plt.show()


    # Speedup Graph

    plt.figure(figsize=(8, 5))

    plt.bar(methods, speedups)

    plt.xlabel("Technique")
    plt.ylabel("Speedup")

    plt.title("Speedup Comparison")

    plt.show()