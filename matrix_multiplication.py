import time
from multiprocessing import Pool, cpu_count
import random

N = 500

# Using a fixed seed so that Windows child processes 
# generate the exact same random matrices as the main process.
random.seed(42)

# Global matrices setup
A = [[random.random() for _ in range(N)] for _ in range(N)]
B = [[random.random() for _ in range(N)] for _ in range(N)]

# Pre-computing columns of B makes multiplication much faster
B_cols = list(zip(*B))

def multiply_row(row_A):
    # Now it uses the pre-computed B_cols
    return [sum(a * b for a, b in zip(row_A, col)) for col in B_cols]

if __name__ == "__main__":
    workers = cpu_count()
    print(f"Matrix size     : {N}x{N}\nCPU cores       : {workers}\n")

    # Sequential Processing
    t1 = time.time()
    seq_res = [multiply_row(row) for row in A]
    seq_time = time.time() - t1
    print(f"Sequential time      : {seq_time:.4f} sec")

    # Parallel Processing
    t2 = time.time()
    with Pool(workers) as pool:
        par_res = pool.map(multiply_row, A, chunksize=(N // workers) + 1)
    par_time = time.time() - t2
    print(f"Multiprocessing time : {par_time:.4f} sec\n")

    print(f"Speedup   : {seq_time / par_time:.2f}x")
    print(f"Efficiency: {seq_time / par_time / workers * 100:.2f}%")

    assert seq_res == par_res, "Results do not match!"
    print("\nResult verified : both methods give same result")