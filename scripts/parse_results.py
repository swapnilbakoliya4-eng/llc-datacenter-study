#!/usr/bin/env python3
import os
import re
import csv

dump_dir = "results/raw_dumps"
out_csv = "results/summary.csv"
rows = []

for fname in sorted(os.listdir(dump_dir)):
    if not fname.endswith(".txt"):
        continue

    parts = fname[:-4].split("_")
    policy = parts[-1].upper()
    workload = "_".join(parts[:-1])

    ipc, cycles, instructions = 0.0, 0, 0
    accesses, hits, misses = 0, 0, 0

    with open(os.path.join(dump_dir, fname)) as f:
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

    hit_rate = (hits / accesses * 100.0) if accesses else 0.0
    mpki = (misses / (instructions / 1000.0)) if instructions else 0.0
    rows.append([workload, policy, instructions, cycles, ipc, accesses, hits, misses, round(hit_rate, 2), round(mpki, 2)])

headers = ["workload", "policy", "instructions", "cycles", "ipc", "llc_access", "llc_hit", "llc_miss", "hit_rate_pct", "mpki"]
with open(out_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(headers)
    w.writerows(rows)

print(f"{'Workload':<16} {'Policy':<8} {'IPC':<8} {'Hits':<8} {'Misses':<10} {'Hit%':<8} {'MPKI':<6}")
print("-" * 68)
for r in rows:
    print(f"{r[0]:<16} {r[1]:<8} {r[4]:<8.4f} {r[6]:<8} {r[7]:<10} {r[8]:<8.2f} {r[9]:<6.2f}")
