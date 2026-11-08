#!/usr/bin/env python3
"""Validate all benchmark rows, summarize medians, and draw charts from actual CSV data."""
import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from statistics import median

os.environ.setdefault("MPLCONFIGDIR", "/tmp/daa-assignment4-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
COUNTERS = ["calls", "states", "comparisons", "lps_comparisons", "peak_array_cells", "max_depth"]
LABELS = {"recursive": "Recursive", "table": "Full table", "two_rows": "Two rows", "naive": "Naive", "kmp": "KMP (search + LPS)"}
COLORS = {"recursive": "#b34430", "table": "#225fa3", "two_rows": "#148066", "naive": "#b34430", "kmp": "#225fa3"}


def expected_cases():
    cases = set()
    for n in [3, 6, 9, 12, 128, 256, 512, 1024, 2048]:
        for kind in ["identical", "disjoint"]:
            for algorithm in (["recursive"] if n <= 12 else []) + ["table", "two_rows"]:
                cases.add((algorithm, kind, n, n))
    for n in [4096, 16384, 65536, 262144]:
        for kind in ["random", "near_match"]:
            for algorithm in ["naive", "kmp"]:
                cases.add((algorithm, kind, n, n // 64))
    return cases


def summarize():
    groups = defaultdict(list)
    fingerprints = {}
    with (ROOT / "results/results.csv").open(newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 300:
        raise ValueError(f"Expected 300 measured rows, found {len(rows)}")
    for row in rows:
        key = row["algorithm"], row["input"], int(row["n"]), int(row["m"])
        groups[key].append(row)
        assert int(row["seed"]) == 20261108
        assert float(row["time_ms"]) > 0
        assert all(int(row[c]) >= 0 for c in COUNTERS)
        assert len(row["input_sha256"]) == 64
        case = key[1:]
        if case in fingerprints:
            assert fingerprints[case] == row["input_sha256"]
        fingerprints[case] = row["input_sha256"]
    assert set(groups) == expected_cases(), "Missing or unexpected cases"
    summary = []
    for (algorithm, kind, n, m), samples in sorted(groups.items()):
        assert sorted(int(r["run"]) for r in samples) == [1, 2, 3, 4, 5]
        assert len({tuple(r[c] for c in COUNTERS + ["result", "input_sha256"]) for r in samples}) == 1
        first = samples[0]
        result = {"algorithm": algorithm, "input": kind, "n": n, "m": m,
                  "time_ms": median(float(r["time_ms"]) for r in samples),
                  "min_time_ms": min(float(r["time_ms"]) for r in samples),
                  "max_time_ms": max(float(r["time_ms"]) for r in samples),
                  "result": int(first["result"])}
        result.update({c: int(first[c]) for c in COUNTERS})
        result["total_comparisons"] = result["comparisons"] + result["lps_comparisons"]
        if algorithm in ["table", "two_rows"]:
            assert result["states"] == n * m
            assert result["peak_array_cells"] == ((n + 1) * (m + 1) if algorithm == "table" else 2 * (m + 1))
        if algorithm == "naive" and kind == "near_match":
            assert result["comparisons"] == (n - m + 1) * m
        if algorithm == "kmp":
            assert result["total_comparisons"] <= 2 * (n + m)
        summary.append(result)
    with (ROOT / "results/summary.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    (ROOT / "results/analysis.json").write_text(json.dumps({"measured_rows": len(rows), "cases": len(summary), "summary": summary}, indent=2) + "\n")
    return summary


def series(summary, algorithm, kind, metric, small=False):
    values = [r for r in summary if r["algorithm"] == algorithm and r["input"] == kind]
    if algorithm in ["table", "two_rows"]:
        values = [r for r in values if (r["n"] <= 12) == small]
    values.sort(key=lambda r: r["n"])
    return [r["n"] for r in values], [r[metric] for r in values]


def decorate(ax, title, ylabel, xlabel="Input length n (characters)"):
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)


def save(fig, name):
    fig.tight_layout(pad=1.1)
    fig.savefig(ROOT / "results/plots" / name, dpi=180, facecolor="white")
    plt.close(fig)


def plot(summary):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "legend.fontsize": 8})
    (ROOT / "results/plots").mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 2.65))
    for kind, style in [("disjoint", "-"), ("identical", "--")]:
        x, y = series(summary, "recursive", kind, "states")
        ax.plot(x, y, style + "o", color=COLORS["recursive"], label=f"Recursive / {kind}")
    x, y = series(summary, "table", "disjoint", "states", small=True)
    ax.plot(x, y, "-s", color=COLORS["table"], label="Both DP versions / either input")
    ax.set_yscale("log")
    ax.set_xticks([3, 6, 9, 12])
    decorate(ax, "Edit Distance: repeated states dominate recursion", "Non-base state evaluations (count)")
    ax.legend(loc="upper left")
    save(fig, "01_edit_work.png")

    fig, ax = plt.subplots(figsize=(9, 2.65))
    for algorithm in ["table", "two_rows"]:
        x, y = series(summary, algorithm, "disjoint", "peak_array_cells")
        ax.plot(x, y, "-o", color=COLORS[algorithm], label=LABELS[algorithm])
    ax.set_xscale("log", base=2); ax.set_yscale("log", base=2)
    decorate(ax, "DP storage: same answer, different retained state", "Peak live int-array cells (count)")
    ax.legend(loc="upper left")
    save(fig, "02_dp_storage.png")

    fig, ax = plt.subplots(figsize=(9, 2.65))
    for algorithm in ["naive", "kmp"]:
        for kind, style in [("near_match", "-"), ("random", "--")]:
            x, y = series(summary, algorithm, kind, "total_comparisons")
            ax.plot(x, y, style + "o", color=COLORS[algorithm], label=f"{LABELS[algorithm]} / {kind.replace('_', ' ')}")
    ax.set_xscale("log", base=2); ax.set_yscale("log")
    decorate(ax, "String search: near matches expose Naive's worst case", "Character comparisons (count)", "Text length n (characters); pattern m = n/64")
    ax.legend(loc="upper left", ncol=2)
    save(fig, "03_search_work.png")

    fig, axes = plt.subplots(1, 2, figsize=(9, 2.65))
    for algorithm in ["table", "two_rows"]:
        x, y = series(summary, algorithm, "disjoint", "time_ms")
        axes[0].plot(x, y, "-o", color=COLORS[algorithm], label=LABELS[algorithm])
    for algorithm in ["naive", "kmp"]:
        x, y = series(summary, algorithm, "near_match", "time_ms")
        axes[1].plot(x, y, "-o", color=COLORS[algorithm], label=LABELS[algorithm])
    for ax, title in zip(axes, ["Disjoint Edit Distance", "Near-match string search"]):
        ax.set_xscale("log", base=2); ax.set_yscale("log")
        decorate(ax, title, "Median elapsed time (ms)")
        ax.legend()
    save(fig, "04_median_time.png")


if __name__ == "__main__":
    summary = summarize()
    plot(summary)
    print(f"Validated 300 rows / {len(summary)} cases; wrote summaries and four PNG plots.")
