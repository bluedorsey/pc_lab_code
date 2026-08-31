# Odd / Even Counting - Sequential vs Multiprocessing
# Counts how many odd and even numbers are there from 0 to N

import time
from multiprocessing import Pool, cpu_count

N = 100000000  # 10 crore numbers


def count_range(args):
    # counts odd and even numbers between start and end
    # if we pass the full range -> it becomes normal sequential counting
    start, end = args
    odd = 0
    even = 0
    for i in range(start, end):
        if i % 2 == 0:
            even += 1
        else:
            odd += 1
    return odd, even


def sequential(n):
    return count_range((0, n))


def parallel(n, workers):
    # divide the range into equal parts, one part for each process
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = n if p == workers - 1 else start + chunk
        tasks.append((start, end))

    with Pool(workers) as pool:
        parts = pool.map(count_range, tasks)

    # add up the counts returned by all the processes
    odd = 0
    even = 0
    for o, e in parts:
        odd += o
        even += e
    return odd, even


if __name__ == "__main__":
    workers = cpu_count()
    print("Numbers   :", N)
    print("CPU cores :", workers)
    print()

    t1 = time.time()
    r1 = sequential(N)
    seq_time = time.time() - t1
    print("Sequential time      : %.2f sec" % seq_time)

    t2 = time.time()
    r2 = parallel(N, workers)
    par_time = time.time() - t2
    print("Multiprocessing time : %.2f sec" % par_time)

    print()
    print("Odd numbers  :", r1[0])
    print("Even numbers :", r1[1])
    print()
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    assert r1 == r2, "results do not match!"
    print("Result verified : both methods give same count")
