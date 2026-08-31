# Matrix Multiplication - Sequential vs Multiprocessing
# Matrix size 500 x 500

import random
import time
from multiprocessing import Pool, cpu_count

N = 500


def make_matrix(n):
    # create n x n matrix filled with random numbers
    return [[random.random() for _ in range(n)] for _ in range(n)]


def multiply_rows(args):
    # multiplies the given rows of A with the full matrix B
    # if we pass all rows -> it becomes normal sequential multiplication
    rows, B = args
    n = len(B)
    result = []
    for i in range(len(rows)):
        new_row = [0] * n
        for j in range(n):
            total = 0
            for k in range(n):
                total += rows[i][k] * B[k][j]
            new_row[j] = total
        result.append(new_row)
    return result


def sequential(A, B):
    return multiply_rows((A, B))


def parallel(A, B, workers):
    # divide the rows of A into equal parts, one part for each process
    chunk = len(A) // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = len(A) if p == workers - 1 else start + chunk
        tasks.append((A[start:end], B))

    with Pool(workers) as pool:
        parts = pool.map(multiply_rows, tasks)

    # join all the row blocks back into one matrix
    C = []
    for part in parts:
        C += part
    return C


if __name__ == "__main__":
    workers = cpu_count()
    print("Matrix size :", N, "x", N)
    print("CPU cores   :", workers)
    print()

    A = make_matrix(N)
    B = make_matrix(N)

    t1 = time.time()
    C1 = sequential(A, B)
    seq_time = time.time() - t1
    print("Sequential time      : %.2f sec" % seq_time)

    t2 = time.time()
    C2 = parallel(A, B, workers)
    par_time = time.time() - t2
    print("Multiprocessing time : %.2f sec" % par_time)

    print()
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    # both answers must be same
    assert C1 == C2, "results do not match!"
    print("Result verified : both matrices are same")
