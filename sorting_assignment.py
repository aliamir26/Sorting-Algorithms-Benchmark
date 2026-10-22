"""
Sorting Algorithms on Real-World Big Data
Assignment: Bubble Sort, Selection Sort & Insertion Sort

Dataset: Airline Delay and Cancellation Data, 2009-2018 (Kaggle)
https://www.kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018

Author: Ali Amir
Roll No: 24F-0622
"""

import os
import time
import random
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # lets charts be saved even without a screen
import matplotlib.pyplot as plt

# CONFIG - change these values for your own run

DEMO_MODE = False          # False when running for real on Kaggle
RANDOM_SEED = 42          
YEARS_TO_USE = ["2013"]  
CHUNK_SIZE = 1_000_000    

SAMPLE_SIZES = [100, 500, 1000, 2000, 4000]

MAX_SECONDS_PER_RUN = 30

NUMERIC_COLUMN = "ARR_DELAY"   # chosen numeric column (Part A2)
TEXT_COLUMN = "OP_CARRIER"     # chosen text column (Part A2)

random.seed(RANDOM_SEED)



def find_kaggle_dataset_path():
    base = "/kaggle/input"
    if not os.path.isdir(base):
        return None
    for root, dirs, files in os.walk(base):
        if "airline" in root.lower() and files:
            return root
        depth = root[len(base):].count(os.sep)
        if depth > 4:
            dirs[:] = []
    return None
    
# PART A - DATA LOADING & EXPLORATION

def load_data():
    """
    Loads the chosen portion of the dataset using CHUNKED reading, so we
    never hold the entire multi-gigabyte file in RAM at once.

    Returns: (dataframe, total_rows, columns, one_chunk_memory_mb)
    """
    if DEMO_MODE:
        print("[DEMO MODE] Using a small fake dataset instead of the real Kaggle files.")
        df = make_fake_dataset()
        chunk_mem_mb = df.memory_usage(deep=True).sum() / 1e6
        return df, len(df), list(df.columns), chunk_mem_mb

    # --- REAL MODE ---
    base = find_kaggle_dataset_path()
    if base is None:
        available = os.listdir("/kaggle/input") if os.path.isdir("/kaggle/input") else []
        raise FileNotFoundError(
            "Dataset not found under /kaggle/input/. Folders currently attached: "
            f"{available}. Click '+ Add Input' in the right sidebar, search for "
            "'Airline Delay and Cancellation Data, 2009-2018', add it, then re-run this cell.")

    print("Using dataset folder:", base)
    print("Files found:")
    for f in sorted(os.listdir(base)):
        size_mb = os.path.getsize(os.path.join(base, f)) / 1e6
        print(f"  {f}  ({size_mb:.1f} MB)")

    all_chunks = []
    total_rows = 0
    chunk_mem_mb = None
    columns = None

    for year in YEARS_TO_USE:
        path = os.path.join(base, f"{year}.csv")
        print(f"\nReading {path} in chunks of {CHUNK_SIZE} rows...")
        for i, chunk in enumerate(pd.read_csv(path, chunksize=CHUNK_SIZE)):
            # We only report the memory of the first chunk, as a sample
            if chunk_mem_mb is None:
                chunk_mem_mb = chunk.memory_usage(deep=True).sum() / 1e6
                columns = list(chunk.columns)
            total_rows += len(chunk)
            # We do not store the whole chunk, only a small random sample,
            # so less memory is used (we only need data for sampling).
            keep_n = min(len(chunk), 20_000)
            all_chunks.append(chunk.sample(n=keep_n, random_state=RANDOM_SEED))
            print(f"  chunk {i+1} processed, running total rows = {total_rows:,}")

    df = pd.concat(all_chunks, ignore_index=True)
    return df, total_rows, columns, chunk_mem_mb


def explore_data(df, total_rows, columns, chunk_mem_mb):
    """Part A1 + A3: report row count, columns, memory, and numeric stats."""
    print("\n" + "=" * 60)
    print("PART A - DATA EXPLORATION")
    print("=" * 60)
    print("Total rows in chosen portion of dataset:", f"{total_rows:,}")
    print("Columns:", columns)
    print(f"Memory footprint of one chunk: {chunk_mem_mb:.2f} MB")

    print(f"\nChosen numeric column: {NUMERIC_COLUMN}")
    print(f"Chosen text column: {TEXT_COLUMN}")

    col = df[NUMERIC_COLUMN]
    missing_pct = col.isna().mean() * 100
    stats = {
        "min": col.min(),
        "max": col.max(),
        "mean": col.mean(),
        "percent_missing": missing_pct,
    }
    print(f"\nStatistics for {NUMERIC_COLUMN}:")
    for k, v in stats.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")

    return stats

# PART B - BUILDING SAMPLES

def make_sample_orderings(df, column, n):

    values = df[column].dropna().sample(n=n, random_state=RANDOM_SEED).tolist()

    random_order = values.copy()
    random.shuffle(random_order)  # so the order is shuffled differently each time

    sorted_order = sorted(values)          # best case input
    reverse_order = sorted(values, reverse=True)  # worst case input

    return {
        "random": random_order,
        "sorted": sorted_order,
        "reversed": reverse_order,
    }


# PART C - SORTING ALGORITHMS (implemented from scratch)

def bubble_sort(arr):
    """
    Bubble Sort.
    Best case: O(n)       - array already sorted (with early-exit optimization)
    Average case: O(n^2)
    Worst case: O(n^2)     - array in reverse order
    Stable: Yes (equal elements never swap past each other)
    """
    arr = arr.copy()  # copy the list so the original is not changed
    n = len(arr)
    for i in range(n):
        swapped = False
        # After each pass, the largest element reaches its correct place,
        # so we do not need to check it again (n - i - 1)
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            # If no swap happened in this pass, the array is already sorted
            break
    return arr


def selection_sort(arr):
    """
    Selection Sort.
    Best case: O(n^2)
    Average case: O(n^2)
    Worst case: O(n^2)
    Stable: No (can swap equal elements past each other)
    """
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        min_index = i
        # Find the smallest element in the remaining unsorted part
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


def insertion_sort(arr):
    """
    Insertion Sort.
    Best case: O(n)        - array already sorted
    Average case: O(n^2)
    Worst case: O(n^2)     - array in reverse order
    Stable: Yes
    """
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Compare the current element with the elements on its left
        # and shift the bigger elements one place to the right
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


ALGORITHMS = {
    "bubble_sort": bubble_sort,
    "selection_sort": selection_sort,
    "insertion_sort": insertion_sort,
}

# CORRECTNESS TESTS (run before any benchmarking)

def run_correctness_tests():
    print("\n" + "=" * 60)
    print("CORRECTNESS TESTS")
    print("=" * 60)

    test_cases = [
        [5, 3, 8, 1, 9, 2],
        [1, 2, 3, 4, 5],            # already sorted
        [5, 4, 3, 2, 1],            # reverse sorted
        [4, 2, 4, 1, 2, 4],         # duplicates
        ["banana", "apple", "cherry", "date"],  # strings
        [7],                        # single element
        [],                         # empty list
    ]

    for name, func in ALGORITHMS.items():
        for case in test_cases:
            # sorted() is used here only as a REFERENCE,
            # to check correctness, not inside the algorithm.
            expected = sorted(case)
            result = func(case)
            assert result == expected, f"{name} FAILED on {case}: got {result}"
    print("All correctness tests passed for bubble_sort, selection_sort, insertion_sort.")

# PART D - BENCHMARKING

def benchmark_all(df):
 
    print("\n" + "=" * 60)
    print("PART D - BENCHMARKING")
    print("=" * 60)

    results = []
  
    algo_too_slow = {name: False for name in ALGORITHMS}

    for n in SAMPLE_SIZES:
        orderings = make_sample_orderings(df, NUMERIC_COLUMN, n)
        for ordering_name, data in orderings.items():
            for algo_name, algo_func in ALGORITHMS.items():
                if algo_too_slow[algo_name]:
                    print(f"  SKIPPING n={n} | {ordering_name} | {algo_name} "
                          f"(already exceeded {MAX_SECONDS_PER_RUN}s safety limit at a smaller size)")
                    results.append({
                        "size": n, "ordering": ordering_name, "algorithm": algo_name,
                        "time_seconds": None,
                    })
                    continue

                input_copy = data.copy()
                start = time.perf_counter()
                algo_func(input_copy)
                elapsed = time.perf_counter() - start

                results.append({
                    "size": n,
                    "ordering": ordering_name,
                    "algorithm": algo_name,
                    "time_seconds": elapsed,
                })
                print(f"  n={n:>5} | {ordering_name:>8} | {algo_name:>15} | {elapsed:.6f} sec")

                if elapsed > MAX_SECONDS_PER_RUN:
                    algo_too_slow[algo_name] = True
                    print(f"  -> {algo_name} exceeded the {MAX_SECONDS_PER_RUN}s safety limit at n={n}. "
                          f"Larger sizes for this algorithm will be skipped (not run), not guessed.")

    return pd.DataFrame(results)

def benchmark_text_column(df, n=None):
    """
    Part D4: repeats ONE sample-size benchmark using the text column
    instead of the numeric column, so we can compare string vs number
    sorting speed.
    """
    if n is None:
        n = SAMPLE_SIZES[-2]  # a mid-large size, not the biggest (keep it quick)

    print(f"\nText column benchmark (n={n}) on '{TEXT_COLUMN}':")
    orderings = make_sample_orderings(df, TEXT_COLUMN, n)
    rows = []
    for ordering_name, data in orderings.items():
        for algo_name, algo_func in ALGORITHMS.items():
            input_copy = data.copy()
            start = time.perf_counter()
            algo_func(input_copy)
            elapsed = time.perf_counter() - start
            rows.append({
                "size": n, "ordering": ordering_name,
                "algorithm": algo_name, "time_seconds": elapsed,
                "column_type": "text",
            })
            print(f"  {ordering_name:>8} | {algo_name:>15} | {elapsed:.6f} sec")
    return pd.DataFrame(rows)

# CHARTS

def make_chart_runtime_vs_n(results_df, out_path="runtime_vs_n.png"):
    """Chart 1: runtime vs n for each algorithm, on RANDOM order data."""
    plt.figure(figsize=(8, 5))
    subset = results_df[results_df["ordering"] == "random"]
    for algo_name in ALGORITHMS:
        algo_data = subset[subset["algorithm"] == algo_name].sort_values("size")
        plt.plot(algo_data["size"], algo_data["time_seconds"], marker="o", label=algo_name)
    plt.title("Runtime vs Input Size (n) - Random Order Data")
    plt.xlabel("n (number of elements)")
    plt.ylabel("time (seconds)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved chart: {out_path}")


def make_chart_insertion_cases(results_df, out_path="insertion_sort_cases.png"):
    """Chart 2: insertion sort runtime for random vs sorted vs reversed input."""
    plt.figure(figsize=(8, 5))
    subset = results_df[results_df["algorithm"] == "insertion_sort"]
    for ordering_name in ["random", "sorted", "reversed"]:
        data = subset[subset["ordering"] == ordering_name].sort_values("size")
        plt.plot(data["size"], data["time_seconds"], marker="o", label=ordering_name)
    plt.title("Insertion Sort: Random vs Sorted vs Reversed Input")
    plt.xlabel("n (number of elements)")
    plt.ylabel("time (seconds)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved chart: {out_path}")

# PART E - FULL-SCALE EXTRAPOLATION

def extrapolate_full_scale(results_df, total_rows_full_dataset):
    print("\n" + "=" * 60)
    print("PART E - FULL-SCALE EXTRAPOLATION (estimated, not measured)")
    print("=" * 60)

    biggest_n = max(SAMPLE_SIZES)
    random_data = results_df[(results_df["ordering"] == "random") & (results_df["size"] == biggest_n)]

    estimates = {}
    for algo_name in ALGORITHMS:
        row = random_data[random_data["algorithm"] == algo_name].iloc[0]
        measured_time = row["time_seconds"]
        # time = c * n^2  ->  c = time / n^2
        c = measured_time / (biggest_n ** 2)
        estimated_full_time_sec = c * (total_rows_full_dataset ** 2)
        estimates[algo_name] = estimated_full_time_sec
        print(f"{algo_name}: measured {measured_time:.6f}s at n={biggest_n} "
              f"-> c={c:.3e} -> estimated full-scale = {format_seconds(estimated_full_time_sec)}")

    # Timsort (Python's built-in sorted()) comparison - actually MEASURE this
    # on the largest sample, then extrapolate using n*log(n) scaling.
    import math
    sample_values = results_df[(results_df["ordering"] == "random") &
                                (results_df["size"] == biggest_n) &
                                (results_df["algorithm"] == "bubble_sort")]
    # (we just need any list of that size - re-generate one quickly)
    dummy = list(range(biggest_n))
    random.shuffle(dummy)
    start = time.perf_counter()
    sorted(dummy)
    timsort_measured = time.perf_counter() - start
    c_timsort = timsort_measured / (biggest_n * math.log2(max(biggest_n, 2)))
    timsort_full_estimate = c_timsort * total_rows_full_dataset * math.log2(max(total_rows_full_dataset, 2))

    print(f"\nPython sorted() (Timsort): measured {timsort_measured:.6f}s at n={biggest_n} "
          f"-> estimated full-scale = {format_seconds(timsort_full_estimate)}")

    print("\nEstimated speedup factor of Timsort vs each algorithm on full data:")
    for algo_name, est_time in estimates.items():
        speedup = est_time / timsort_full_estimate if timsort_full_estimate > 0 else float("inf")
        print(f"  {algo_name}: ~{speedup:,.0f}x slower than Timsort")

    return estimates, timsort_full_estimate


def format_seconds(seconds):
    """Turns a raw seconds value into a human-readable unit (helper only)."""
    minute, hour, day, year = 60, 3600, 86400, 31_536_000
    if seconds < minute:
        return f"{seconds:.2f} seconds"
    elif seconds < hour:
        return f"{seconds/minute:.2f} minutes"
    elif seconds < day:
        return f"{seconds/hour:.2f} hours"
    elif seconds < year:
        return f"{seconds/day:.2f} days"
    else:
        return f"{seconds/year:.2f} years"




# Part A
df, total_rows, columns, chunk_mem_mb = load_data()
explore_data(df, total_rows, columns, chunk_mem_mb)


run_correctness_tests()


results_df = benchmark_all(df)


text_results_df = benchmark_text_column(df)


results_df.to_csv("sort_benchmark_results.csv", index=False)
print("\nSaved: sort_benchmark_results.csv")

make_chart_runtime_vs_n(results_df)
make_chart_insertion_cases(results_df)


extrapolate_full_scale(results_df, total_rows)
