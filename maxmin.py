# Max and Min of an array - Sequential vs Multiprocessing
# Idea : max/min of the whole array = max/min of the answers of every piece.
# So each process scans its own piece and we compare only a few values at the end.
#
# Note : the array is kept in SHARED MEMORY and every process is given only the
# start/end index of its piece. If we send the array itself to the processes,
# copying it takes more time than scanning it and parallel becomes slower.

import os
import time
from multiprocessing import Pool, cpu_count, shared_memory

N = 40000000
ITEM = 8  # each number is stored in 8 bytes (unsigned long long)


def max_min(args):
    # scans the piece of the shared array from start to end
    # if we pass the full range -> it becomes normal sequential scanning
    name, start, end = args
    shm = shared_memory.SharedMemory(name=name)
    data = shm.buf.cast("Q")

    big = data[start]
    small = data[start]
    for i in range(start, end):
        x = data[i]
        if x > big:
            big = x
        elif x < small:
            small = x

    del data
    shm.close()
    return big, small


def sequential(name, n):
    return max_min((name, 0, n))


def parallel(name, n, workers):
    # divide the array into equal pieces, one piece for each process
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = n if p == workers - 1 else start + chunk
        tasks.append((name, start, end))

    with Pool(workers) as pool:
        parts = pool.map(max_min, tasks)

    # now just compare the max/min returned by each process
    big = parts[0][0]
    small = parts[0][1]
    for b, s in parts:
        if b > big:
            big = b
        if s < small:
            small = s
    return big, small


if __name__ == "__main__":
    workers = cpu_count()
    print("Array size :", N)
    print("CPU cores  :", workers)
    print()

    # make the array in shared memory and fill it with random values
    shm = shared_memory.SharedMemory(create=True, size=N * ITEM)
    shm.buf[:] = os.urandom(N * ITEM)

    try:
        t1 = time.time()
        r1 = sequential(shm.name, N)
        seq_time = time.time() - t1
        print("Sequential time      : %.2f sec" % seq_time)

        t2 = time.time()
        r2 = parallel(shm.name, N, workers)
        par_time = time.time() - t2
        print("Multiprocessing time : %.2f sec" % par_time)

        print()
        print("Maximum :", r1[0])
        print("Minimum :", r1[1])
        print()
        print("Speedup   : %.2fx" % (seq_time / par_time))
        print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

        assert r1 == r2, "results do not match!"
        print("Result verified : both methods give same max and min")
    finally:
        shm.close()
        shm.unlink()
