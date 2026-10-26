#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt
import numpy as np

data = {}
with open("results/summary.csv") as f:
    for row in csv.DictReader(f):
        w = row["workload"]
        p = row["policy"].upper()
        if w not in data:
            data[w] = {}
        hits = int(row["llc_hit"])
        misses = int(row["llc_miss"])
        total = hits + misses
        miss_rate = (misses / total) if total else 1.0
        # 20 cycles LLC hit + 150 cycles DRAM penalty
        amat = 20.0 + (miss_rate * 150.0)
        data[w][p] = amat

policies = ["LRU", "SRRIP", "DRRIP", "SHIP"]
colors = ["#a8c6e5", "#629cd6", "#2362a2", "#0c2340"]
x = np.arange(len(policies))
bar_width = 0.55

plt.rcParams.update({"font.size": 11, "figure.autolayout": True})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 4.0))

gcc_amat = [data["spec_gcc"][p] for p in policies]
b1 = ax1.bar(x, gcc_amat, bar_width, color=colors, edgecolor="black", linewidth=0.6)
ax1.set_title("SPEC CPU 2017: 602.gcc_s", fontweight="bold")
ax1.set_ylabel("AMAT (Cycles) [Lower is Better]")
ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylim(169.0, 170.5)
ax1.grid(axis="y", linestyle="--", alpha=0.4)
ax1.bar_label(b1, fmt="%.2f", padding=2, fontsize=8.5)

gdc_amat = [data["google_arizona"][p] for p in policies]
b2 = ax2.bar(x, gdc_amat, bar_width, color=colors, edgecolor="black", linewidth=0.6)
ax2.set_title("Google DC: arizona_0000", fontweight="bold")
ax2.set_ylabel("AMAT (Cycles) [Lower is Better]")
ax2.set_xticks(x)
ax2.set_xticklabels(policies)
ax2.set_ylim(120.0, 130.0)
ax2.grid(axis="y", linestyle="--", alpha=0.4)
ax2.bar_label(b2, fmt="%.2f", padding=2, fontsize=8.5)

plt.savefig("results/plots/amat_comparison.png", dpi=300)
plt.close()
print("Saved results/plots/amat_comparison.png")
