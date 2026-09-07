# Prime numbers in first N natural numbers - Sequential vs Multiprocessing
# Idea : checking one number for prime does not depend on any other number,
# so the range 1..N can be cut into pieces and every process checks its own piece.

import time
from multiprocessing import Pool, cpu_count

N = 2000000


def is_prime(n):
    # simple trial division method
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def count_primes(args):
    # counts how many primes are there between start and end
    # if we pass the full range -> it becomes normal sequential checking
    start, end = args
    count = 0
    for n in range(start, end):
        if is_prime(n):
            count += 1
    return count


def sequential(n):
    return count_primes((1, n + 1))


def parallel(n, workers):
    # divide 1..N into equal parts, one part for each process
    # ponytail: equal ranges, so the last process gets the bigger numbers and
    # takes a little more time; use smaller chunks if better balance is needed
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = 1 + p * chunk
        end = n + 1 if p == workers - 1 else start + chunk
        tasks.append((start, end))

    with Pool(workers) as pool:
        parts = pool.map(count_primes, tasks)

    # add up the counts returned by all the processes
    count = 0
    for c in parts:
        count += c
    return count


if __name__ == "__main__":
    workers = cpu_count()
    print("Natural numbers :", N)
    print("CPU cores       :", workers)
    print()

    t1 = time.time()
    c1 = sequential(N)
    seq_time = time.time() - t1
    print("Sequential time      : %.2f sec" % seq_time)

    t2 = time.time()
    c2 = parallel(N, workers)
    par_time = time.time() - t2
    print("Multiprocessing time : %.2f sec" % par_time)

    print()
    print("Total prime numbers :", c1)
    print("First 10 primes     :", [n for n in range(1, 30) if is_prime(n)])
    print()
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    assert c1 == c2, "results do not match!"
    print("Result verified : both methods give same prime count")
