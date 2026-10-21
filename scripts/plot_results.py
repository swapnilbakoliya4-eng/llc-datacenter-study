#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt
import numpy as np

# Load summary metrics
data = {}
with open("results/summary.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
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

# Aesthetic 4-shade architectural blue palette (light ice blue -> midnight navy)
colors = ["#A8C6E5", "#629CD6", "#2362A2", "#0C2340"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8
})

# ==========================================================
# Figure 1: IPC Comparison (Dedicated subplots per workload)
# ==========================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 4.2))

x = np.arange(len(policies))
width = 0.55

# Subplot 1: SPEC GCC (Zoomed Y-axis: 0.284 to 0.294)
gcc_ipcs = [data["spec_gcc"][p]["ipc"] for p in policies]
bars1 = ax1.bar(x, gcc_ipcs, width, color=colors, edgecolor="#222222", linewidth=0.6)
ax1.set_title("SPEC CPU 2017: 602.gcc_s", fontweight="bold", fontsize=11)
ax1.set_ylabel("Cumulative IPC")
ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylim(0.284, 0.294)
ax1.grid(axis="y", linestyle="--", alpha=0.4)
ax1.bar_label(bars1, fmt="%.4f", padding=3, fontsize=8.5)

# Subplot 2: Google DC (Zoomed Y-axis: 0.940 to 0.952)
gdc_ipcs = [data["google_arizona"][p]["ipc"] for p in policies]
bars2 = ax2.bar(x, gdc_ipcs, width, color=colors, edgecolor="#222222", linewidth=0.6)
ax2.set_title("Google DC: arizona_0000", fontweight="bold", fontsize=11)
ax2.set_xticks(x)
ax2.set_xticklabels(policies)
ax2.set_ylim(0.940, 0.952)
ax2.grid(axis="y", linestyle="--", alpha=0.4)
ax2.bar_label(bars2, fmt="%.4f", padding=3, fontsize=8.5)

plt.suptitle("Instructions Per Cycle (IPC) by Replacement Policy (2MB LLC)", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("results/plots/ipc_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

# ==========================================================
# Figure 2: Hit Rate and MPKI (3-panel breakdown)
# ==========================================================
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12.5, 4.0))

# Panel 1: Google DC Hit Rate (Highlights the SRRIP drop & recovery)
gdc_hr = [data["google_arizona"][p]["hit_rate"] for p in policies]
bars_hr_gdc = ax1.bar(x, gdc_hr, width, color=colors, edgecolor="#222222", linewidth=0.6)
ax1.set_title("Google DC: LLC Hit Rate (%)", fontweight="bold", fontsize=10.5)
ax1.set_ylabel("Hit Rate (%)")
ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylim(25.0, 34.0)
ax1.grid(axis="y", linestyle="--", alpha=0.4)
ax1.bar_label(bars_hr_gdc, fmt="%.2f%%", padding=3, fontsize=8.5)

# Panel 2: SPEC GCC Hit Rate (Shows capacity thrashing regime)
gcc_hr = [data["spec_gcc"][p]["hit_rate"] for p in policies]
bars_hr_gcc = ax2.bar(x, gcc_hr, width, color=colors, edgecolor="#222222", linewidth=0.6)
ax2.set_title("SPEC GCC: LLC Hit Rate (%)", fontweight="bold", fontsize=10.5)
ax2.set_ylabel("Hit Rate (%)")
ax2.set_xticks(x)
ax2.set_xticklabels(policies)
ax2.set_ylim(0.0, 0.25)
ax2.grid(axis="y", linestyle="--", alpha=0.4)
ax2.bar_label(bars_hr_gcc, fmt="%.2f%%", padding=3, fontsize=8.5)

# Panel 3: LLC MPKI across both workloads
w_x = np.arange(2)
bar_w = 0.18
for i, p in enumerate(policies):
    mpki_vals = [data["spec_gcc"][p]["mpki"], data["google_arizona"][p]["mpki"]]
    pos = [idx + i * bar_w - (1.5 * bar_w) for idx in w_x]
    bars_mpki = ax3.bar(pos, mpki_vals, bar_w, label=p, color=colors[i], edgecolor="#222222", linewidth=0.6)
    ax3.bar_label(bars_mpki, fmt="%.1f", padding=2, fontsize=7.5)

ax3.set_title("LLC MPKI by Workload", fontweight="bold", fontsize=10.5)
ax3.set_ylabel("LLC MPKI (Misses / 1K Inst)")
ax3.set_xticks(w_x)
ax3.set_xticklabels(["SPEC GCC", "Google DC"])
ax3.set_ylim(0, 22.0)
ax3.legend(frameon=True, fontsize=8.5)
ax3.grid(axis="y", linestyle="--", alpha=0.4)

plt.suptitle("Last-Level Cache Locality Metrics (2MB LLC)", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("results/plots/hit_rate_mpki.png", dpi=300, bbox_inches="tight")
plt.close()

print("[+] Clean plots generated in results/plots/ using 4-shade blue palette.")
