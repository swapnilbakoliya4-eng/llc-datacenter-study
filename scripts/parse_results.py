#!/usr/bin/env python3
import os
import re
import csv

DUMP_DIR = "results/raw_dumps"
OUT_CSV = "results/summary.csv"

rows = []

for fname in sorted(os.listdir(DUMP_DIR)):
    if not fname.endswith(".txt"):
        continue

    tag = fname[:-4]
    parts = tag.split("_")
    policy = parts[-1].upper()
    workload = "_".join(parts[:-1])

    ipc, cycles, instructions = 0.0, 0, 0
    accesses, hits, misses = 0, 0, 0

    with open(os.path.join(DUMP_DIR, fname), "r") as f:
        for line in f:
            if "CPU 0 cumulative IPC:" in line:
                m = re.search(r"IPC:\s*([0-9.]+)\s+instructions:\s*([0-9]+)\s+cycles:\s*([0-9]+)", line)
                if m:
                    ipc = float(m.group(1))
                    instructions = int(m.group(2))
                    cycles = int(m.group(3))
            elif "cpu0->LLC TOTAL" in line:
                m = re.search(r"ACCESS:\s*([0-9]+)\s+HIT:\s*([0-9]+)\s+MISS:\s*([0-9]+)", line)
                if m:
                    accesses = int(m.group(1))
                    hits = int(m.group(2))
                    misses = int(m.group(3))

    hit_rate = (hits / accesses * 100.0) if accesses > 0 else 0.0
    mpki = (misses / (instructions / 1000.0)) if instructions > 0 else 0.0

    rows.append([workload, policy, instructions, cycles, ipc, accesses, hits, misses, round(hit_rate, 2), round(mpki, 2)])

headers = ["workload", "policy", "instructions", "cycles", "ipc", "llc_access", "llc_hit", "llc_miss", "hit_rate_pct", "mpki"]
with open(OUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"{'Workload':<16} {'Policy':<8} {'IPC':<8} {'LLC Hits':<10} {'LLC Misses':<12} {'Hit Rate %':<12} {'MPKI':<8}")
print("-" * 76)
for r in rows:
    print(f"{r[0]:<16} {r[1]:<8} {r[4]:<8.4f} {r[6]:<10} {r[7]:<12} {r[8]:<12.2f} {r[9]:<8.2f}")
