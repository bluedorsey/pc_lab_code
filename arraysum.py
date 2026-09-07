# Addition of all elements of an array - Sequential vs Multiprocessing
# Idea : total = sum of the partial sums of every piece of the array.
#
# Note : the array is kept in SHARED MEMORY and every process is given only the
# start/end index of its piece. If we send the array itself to the processes,
# copying it takes more time than adding it and parallel becomes slower.

import os
import time
from multiprocessing import Pool, cpu_count, shared_memory

N = 40000000
ITEM = 8  # each number is stored in 8 bytes (unsigned long long)


def partial_sum(args):
    # adds the numbers of the shared array from start to end
    # if we pass the full range -> it becomes normal sequential addition
    name, start, end = args
    shm = shared_memory.SharedMemory(name=name)
    data = shm.buf.cast("Q")

    total = 0
    for i in range(start, end):
        total += data[i]

    del data
    shm.close()
    return total


def sequential(name, n):
    return partial_sum((name, 0, n))


def parallel(name, n, workers):
    # divide the array into equal pieces, one piece for each process
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = n if p == workers - 1 else start + chunk
        tasks.append((name, start, end))

    with Pool(workers) as pool:
        parts = pool.map(partial_sum, tasks)

    # add all the partial sums to get the final total
    total = 0
    for x in parts:
        total += x
    return total


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
        s1 = sequential(shm.name, N)
        seq_time = time.time() - t1
        print("Sequential time      : %.2f sec" % seq_time)

        t2 = time.time()
        s2 = parallel(shm.name, N, workers)
        par_time = time.time() - t2
        print("Multiprocessing time : %.2f sec" % par_time)

        print()
        print("Sum of all elements :", s1)
        print()
        print("Speedup   : %.2fx" % (seq_time / par_time))
        print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

        assert s1 == s2, "results do not match!"
        print("Result verified : both methods give same sum")
    finally:
        shm.close()
        shm.unlink()
