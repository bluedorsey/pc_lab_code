# N Fibonacci numbers - Sequential vs Multiprocessing
# Problem : the normal way (a, b = b, a + b) is purely sequential, F(i) needs
# F(i-1) and F(i-2), so it cannot be divided among processes.
# Solution : the "fast doubling" formula gives any F(k) directly, without making
# the terms before it. Now every term is an independent job, so the terms can be
# divided among the processes and each one works on its own part.

import time
from multiprocessing import Pool, cpu_count

N = 35000


def fib(n):
    # fast doubling : F(2k) = F(k) * (2*F(k+1) - F(k))
    #                 F(2k+1) = F(k)^2 + F(k+1)^2
    return fib_pair(n)[0]


def fib_pair(n):
    # returns (F(n), F(n+1)) directly, without making the whole series
    if n == 0:
        return 0, 1
    a, b = fib_pair(n >> 1)
    c = a * (2 * b - a)
    d = a * a + b * b
    if n & 1:
        return d, c + d
    return c, d


def fib_range(args):
    # finds every fibonacci term from index start to end
    # if we pass the full range -> it becomes normal sequential work
    start, end = args
    return [fib(k) for k in range(start, end)]


def sequential(n):
    return fib_range((0, n))


def parallel(n, workers):
    # divide the n terms into equal parts, one part for each process
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = n if p == workers - 1 else start + chunk
        tasks.append((start, end))

    with Pool(workers) as pool:
        parts = pool.map(fib_range, tasks)

    # join all the pieces of the series in order
    series = []
    for part in parts:
        series += part
    return series


def normal_series(n):
    # the usual sequential method, kept only to check that our answer is correct
    series = []
    a, b = 0, 1
    for _ in range(n):
        series.append(a)
        a, b = b, a + b
    return series


if __name__ == "__main__":
    workers = cpu_count()
    print("Fibonacci terms :", N)
    print("CPU cores       :", workers)
    print()

    t1 = time.time()
    f1 = sequential(N)
    seq_time = time.time() - t1
    print("Sequential time      : %.2f sec" % seq_time)

    t2 = time.time()
    f2 = parallel(N, workers)
    par_time = time.time() - t2
    print("Multiprocessing time : %.2f sec" % par_time)

    print()
    print("First 15 terms :", f1[:15])
    # the last term is a huge number, so we only estimate how many digits it has
    print("Digits in last term :", int(f1[-1].bit_length() * 0.30103) + 1)
    print()
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    assert f1 == f2, "results do not match!"
    assert f1 == normal_series(N), "series is wrong!"
    print("Result verified : both methods give same fibonacci series")
