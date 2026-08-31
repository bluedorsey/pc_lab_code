# Factorial of a big number - Sequential vs Multiprocessing
# Idea : factorial is just 1*2*3*...*N
# So we can break the range into parts, let each process find its own
# partial product, and then multiply all the partial products at the end.

import time
from multiprocessing import Pool, cpu_count

N = 200000


def partial_product(args):
    # multiplies all the numbers between start and end
    # if we pass the full range -> it becomes normal sequential factorial
    start, end = args
    result = 1
    for i in range(start, end):
        result *= i
    return result


def sequential(n):
    return partial_product((1, n + 1))


def parallel(n, workers):
    # divide 1..N into equal parts, one part for each process
    chunk = n // workers
    tasks = []
    for p in range(workers):
        start = 1 + p * chunk
        end = n + 1 if p == workers - 1 else start + chunk
        tasks.append((start, end))

    with Pool(workers) as pool:
        parts = pool.map(partial_product, tasks)

    # multiply all the partial products together to get the final answer
    result = 1
    for x in parts:
        result *= x
    return result


if __name__ == "__main__":
    workers = cpu_count()
    print("Factorial of :", N)
    print("CPU cores    :", workers)
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
    # a 200000! number is huge, so we just estimate how many digits it has
    digits = int(f1.bit_length() * 0.30103) + 1
    print("Total digits in answer :", digits)
    print()
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    assert f1 == f2, "results do not match!"
    print("Result verified : both methods give same factorial")
