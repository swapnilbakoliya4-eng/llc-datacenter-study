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
        data[w][p] = {
            "ipc": float(row["ipc"]),
            "hit_rate": float(row["hit_rate_pct"]),
            "mpki": float(row["mpki"]),
        }

policies = ["LRU", "SRRIP", "DRRIP", "SHIP"]
colors = ["#a8c6e5", "#629cd6", "#2362a2", "#0c2340"]
x = np.arange(len(policies))
bar_width = 0.55

# IPC
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.8))

gcc_ipcs = [data["spec_gcc"][p]["ipc"] for p in policies]
b1 = ax1.bar(x, gcc_ipcs, bar_width, color=colors, edgecolor="black", linewidth=0.5)
ax1.set_title("SPEC GCC (602.gcc_s)")
ax1.set_ylabel("IPC")
ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylim(0.284, 0.294)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.bar_label(b1, fmt="%.4f", padding=2, fontsize=8)

gdc_ipcs = [data["google_arizona"][p]["ipc"] for p in policies]
b2 = ax2.bar(x, gdc_ipcs, bar_width, color=colors, edgecolor="black", linewidth=0.5)
ax2.set_title("Google DC (arizona_0000)")
ax2.set_xticks(x)
ax2.set_xticklabels(policies)
ax2.set_ylim(0.940, 0.952)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
ax2.bar_label(b2, fmt="%.4f", padding=2, fontsize=8)

plt.tight_layout()
plt.savefig("results/plots/ipc_comparison.png", dpi=200)
plt.close()

# Hit rate & MPKI
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3.6))

gdc_hr = [data["google_arizona"][p]["hit_rate"] for p in policies]
b_hr1 = ax1.bar(x, gdc_hr, bar_width, color=colors, edgecolor="black", linewidth=0.5)
ax1.set_title("Google DC Hit Rate (%)")
ax1.set_ylabel("Hit Rate (%)")
ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylim(25.0, 34.0)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.bar_label(b_hr1, fmt="%.2f%%", padding=2, fontsize=8)

gcc_hr = [data["spec_gcc"][p]["hit_rate"] for p in policies]
b_hr2 = ax2.bar(x, gcc_hr, bar_width, color=colors, edgecolor="black", linewidth=0.5)
ax2.set_title("SPEC GCC Hit Rate (%)")
ax2.set_ylabel("Hit Rate (%)")
ax2.set_xticks(x)
ax2.set_xticklabels(policies)
ax2.set_ylim(0.0, 0.25)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
ax2.bar_label(b_hr2, fmt="%.2f%%", padding=2, fontsize=8)

w_x = np.arange(2)
bw = 0.18
for i, p in enumerate(policies):
    vals = [data["spec_gcc"][p]["mpki"], data["google_arizona"][p]["mpki"]]
    pos = [idx + i * bw - (1.5 * bw) for idx in w_x]
    b_mpki = ax3.bar(pos, vals, bw, label=p, color=colors[i], edgecolor="black", linewidth=0.5)
    ax3.bar_label(b_mpki, fmt="%.1f", padding=2, fontsize=7.5)

ax3.set_title("LLC MPKI")
ax3.set_ylabel("MPKI")
ax3.set_xticks(w_x)
ax3.set_xticklabels(["SPEC GCC", "Google DC"])
ax3.set_ylim(0, 22.0)
ax3.legend(fontsize=8)
ax3.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("results/plots/hit_rate_mpki.png", dpi=200)
plt.close()
