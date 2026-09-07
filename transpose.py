# Transpose of a matrix - Sequential vs Multiprocessing
# Idea : row j of the transpose is nothing but column j of the original matrix,
# and no column depends on any other column. So each process is given a block of
# columns and it writes those columns as rows of the answer.
#
# Note : both matrices are kept in SHARED MEMORY as one long line of numbers,
# element (i, j) is at position i * COLS + j. Transpose only moves data, it does
# no calculation, so if we send the matrix to the processes then the copying
# itself takes more time than the transpose and parallel becomes slower.

import os
import time
from multiprocessing import Pool, cpu_count, shared_memory

ROWS = 4000
COLS = 4000
ITEM = 8  # each number is stored in 8 bytes (unsigned long long)


def transpose_block(args):
    # takes the columns from start to end of matrix A
    # and writes them as rows of matrix T
    # if we pass all the columns -> it becomes normal sequential transpose
    src, dst, rows, cols, start, end = args
    a = shared_memory.SharedMemory(name=src)
    t = shared_memory.SharedMemory(name=dst)
    A = a.buf.cast("Q")
    T = t.buf.cast("Q")

    for j in range(start, end):
        row = j * rows            # row j of the transpose
        for i in range(rows):
            T[row + i] = A[i * cols + j]

    del A, T
    a.close()
    t.close()
    return end - start


def sequential(src, dst, rows, cols):
    return transpose_block((src, dst, rows, cols, 0, cols))


def parallel(src, dst, rows, cols, workers):
    # divide the columns into equal parts, one part for each process
    chunk = cols // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = cols if p == workers - 1 else start + chunk
        tasks.append((src, dst, rows, cols, start, end))

    with Pool(workers) as pool:
        pool.map(transpose_block, tasks)


if __name__ == "__main__":
    workers = cpu_count()
    print("Matrix size :", ROWS, "x", COLS)
    print("CPU cores   :", workers)
    print()

    size = ROWS * COLS * ITEM
    a = shared_memory.SharedMemory(create=True, size=size)   # matrix A
    t = shared_memory.SharedMemory(create=True, size=size)   # its transpose
    a.buf[:] = os.urandom(size)

    try:
        t1 = time.time()
        sequential(a.name, t.name, ROWS, COLS)
        seq_time = time.time() - t1
        print("Sequential time      : %.2f sec" % seq_time)

        # keep the sequential answer and clear the matrix before doing it again
        answer = bytes(t.buf)
        t.buf[:] = bytes(size)

        t2 = time.time()
        parallel(a.name, t.name, ROWS, COLS, workers)
        par_time = time.time() - t2
        print("Multiprocessing time : %.2f sec" % par_time)

        A = a.buf.cast("Q")
        T = t.buf.cast("Q")
        print()
        print("Size of transpose :", COLS, "x", ROWS)
        print("Check  A[0][1] :", A[1])
        print("       T[1][0] :", T[ROWS])
        del A, T

        print()
        print("Speedup   : %.2fx" % (seq_time / par_time))
        print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

        assert bytes(t.buf) == answer, "results do not match!"
        print("Result verified : both methods give same transpose")
    finally:
        a.close()
        a.unlink()
        t.close()
        t.unlink()
