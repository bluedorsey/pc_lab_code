# Bubble Sort - Sequential vs Multiprocessing
# Idea : bubble sort takes O(n^2) time, so sorting one big array is very costly.
# In parallel we cut the array into pieces, every process bubble sorts its own
# small piece, and at the end the sorted pieces are merged together.

import random
import time
from heapq import merge
from multiprocessing import Pool, cpu_count

N = 12000


def bubble_sort(arr):
    # normal bubble sort on the given piece of the array
    # if we pass the full array -> it becomes normal sequential bubble sort
    a = list(arr)
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def sequential(arr):
    return bubble_sort(arr)


def parallel(arr, workers):
    # divide the array into equal pieces, one piece for each process
    chunk = len(arr) // workers
    tasks = []
    for p in range(workers):
        start = p * chunk
        end = len(arr) if p == workers - 1 else start + chunk
        tasks.append(arr[start:end])

    with Pool(workers) as pool:
        parts = pool.map(bubble_sort, tasks)

    # every piece is sorted now, so merge them into one sorted list
    return list(merge(*parts))


if __name__ == "__main__":
    workers = cpu_count()
    print("Array size :", N)
    print("CPU cores  :", workers)
    print()

    arr = [random.randint(1, 100000) for _ in range(N)]

    t1 = time.time()
    s1 = sequential(arr)
    seq_time = time.time() - t1
    print("Sequential time      : %.2f sec" % seq_time)

    t2 = time.time()
    s2 = parallel(arr, workers)
    par_time = time.time() - t2
    print("Multiprocessing time : %.2f sec" % par_time)

    print()
    print("First 10 numbers before sorting :", arr[:10])
    print("First 10 numbers after sorting  :", s1[:10])
    print()
    # speedup here is more than the number of cores, because bubble sort is O(n^2)
    # and sorting many small pieces is much cheaper than sorting one big array
    print("Speedup   : %.2fx" % (seq_time / par_time))
    print("Efficiency: %.2f%%" % (seq_time / par_time / workers * 100))

    assert s1 == s2, "results do not match!"
    print("Result verified : both methods give same sorted array")
