"""Benchmark: measure tokens/sec and memory for 1 KB / 10 KB / 100 KB inputs.

Usage:
    python tests/bench_compression.py
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contextcrunch import crunch


def _generate_text(size_kb: int) -> str:
    base = "Please create a function that basically just returns the sum of two numbers. "
    base += "Make sure to use proper error handling and input validation. "
    base += "The function should be efficient and well-documented. "
    base += 'Use the name "calculate_sum" for this function. '
    base += "It should handle edge cases gracefully.\n"
    repeats = max(1, int(size_kb * 1024 / len(base)))
    return (base * repeats)[: size_kb * 1024]


def bench(size_kb: int) -> dict:
    text = _generate_text(size_kb)
    text_size = len(text.encode("utf-8"))

    start = time.perf_counter()
    result = crunch(text, level="safe")
    elapsed = time.perf_counter() - start

    return {
        "input_size_kb": size_kb,
        "input_bytes": text_size,
        "elapsed_sec": round(elapsed, 4),
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "savings_percent": result.savings_percent,
        "tokens_per_sec": round(result.original_tokens / elapsed, 1) if elapsed > 0 else 0,
    }


def main():
    results = []
    for size_kb in [1, 10, 100]:
        print(f"Benchmarking {size_kb} KB input...", end=" ", flush=True)
        r = bench(size_kb)
        results.append(r)
        print(f"done ({r['elapsed_sec']:.2f}s, {r['tokens_per_sec']:.0f} tok/s)")

    print()
    print(f"{'Size':>8} {'Bytes':>10} {'Time':>8} {'OrigTok':>8} {'CompTok':>8} {'Savings':>8} {'Tok/s':>10}")
    print("-" * 62)
    for r in results:
        print(f"{r['input_size_kb']:>4}KB {r['input_bytes']:>10} {r['elapsed_sec']:>7.2f}s "
              f"{r['original_tokens']:>8} {r['compressed_tokens']:>8} "
              f"{r['savings_percent']:>7.1f}% {r['tokens_per_sec']:>10.0f}")


if __name__ == "__main__":
    main()
