#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt

data = {}
with open("results/summary.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        w = row["workload"]
        p = row["policy"]
        if w not in data:
            data[w] = {}
        data[w][p] = {
            "ipc": float(row["ipc"]),
            "hit_rate": float(row["hit_rate_pct"]),
            "mpki": float(row["mpki"])
        }

policies = ["LRU", "SRRIP", "DRRIP"]
workloads = ["spec_gcc", "google_arizona"]
labels = ["SPEC GCC (602.gcc_s)", "Google DC (arizona_0000)"]
x = [0, 1]
width = 0.22

# Plot 1: IPC Comparison
fig, ax = plt.subplots(figsize=(6, 4))
for i, p in enumerate(policies):
    vals = [data[w][p]["ipc"] for w in workloads]
    ax.bar([pos + i * width for pos in x], vals, width, label=p)

ax.set_ylabel("Cumulative IPC")
ax.set_xticks([pos + width for pos in x])
ax.set_xticklabels(labels)
ax.set_title("IPC by Replacement Policy (2MB LLC)")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("results/plots/ipc_comparison.png", dpi=300)
plt.close()

# Plot 2: Hit Rate and MPKI
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for i, p in enumerate(policies):
    hr = [data[w][p]["hit_rate"] for w in workloads]
    mpki = [data[w][p]["mpki"] for w in workloads]
    ax1.bar([pos + i * width for pos in x], hr, width, label=p)
    ax2.bar([pos + i * width for pos in x], mpki, width, label=p)

ax1.set_ylabel("LLC Hit Rate (%)")
ax1.set_xticks([pos + width for pos in x])
ax1.set_xticklabels(labels)
ax1.set_title("LLC Hit Rate (%)")
ax1.legend()
ax1.grid(axis="y", linestyle="--", alpha=0.6)

ax2.set_ylabel("LLC MPKI")
ax2.set_xticks([pos + width for pos in x])
ax2.set_xticklabels(labels)
ax2.set_title("LLC MPKI (Misses / 1K Inst)")
ax2.legend()
ax2.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("results/plots/hit_rate_mpki.png", dpi=300)
plt.close()

print("Generated results/plots/ipc_comparison.png and results/plots/hit_rate_mpki.png")
