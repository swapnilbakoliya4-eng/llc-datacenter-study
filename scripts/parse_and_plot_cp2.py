import glob, re, os, csv
import numpy as np
import matplotlib.pyplot as plt

rows = []
for path in sorted(glob.glob("results/logs_cp2/*.log")):
    base = os.path.basename(path).replace(".log", "")
    pol, size, trace = base.split("_", 2)
    txt = open(path).read()

    ipc_m = re.search(r"CPU 0 cumulative IPC:\s+([0-9.]+)", txt)
    llc_m = re.search(r"LLC TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)", txt)

    if ipc_m and llc_m:
        ipc = float(ipc_m.group(1))
        acc, hit, miss = map(int, llc_m.groups())
        hr = (hit / acc * 100.0) if acc > 0 else 0.0
        mpki = miss / 10000.0
        suite = "SPEC17" if trace[0].isdigit() else "Google_DC"
        rows.append({
            "policy": pol, "size": size, "trace": trace, "suite": suite,
            "ipc": ipc, "hit_rate": hr, "mpki": mpki,
            "access": acc, "hit": hit, "miss": miss
        })

csv_path = "results/cp2_results.csv"
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["policy", "size", "trace", "suite", "ipc", "hit_rate", "mpki", "access", "hit", "miss"])
    w.writeheader()
    w.writerows(rows)
print(f"Saved {len(rows)} rows to {csv_path}")

policies = ["lru", "srrip", "drrip", "ship", "hawkeye", "mockingjay"]
labels = ["LRU", "SRRIP", "DRRIP", "SHiP", "Hawkeye", "Mockingjay"]
colors = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3", "#937860"]

data = {(r["policy"], r["size"], r["trace"]): r for r in rows}
traces_12 = [l.strip().split("/")[-1].split(".")[0] for l in open("traces_12.txt") if l.strip()]
short_names = [t.split("-")[0].replace("_0000", "") for t in traces_12]

# Plot 1: LLC Hit Rate (2MB)
fig, ax = plt.subplots(figsize=(13, 5))
x = np.arange(len(traces_12))
w = 0.13
for i, (pol, lbl, col) in enumerate(zip(policies, labels, colors)):
    vals = [data[(pol, "2mb", t)]["hit_rate"] if (pol, "2mb", t) in data else 0 for t in traces_12]
    ax.bar(x + (i - 2.5) * w, vals, width=w, label=lbl, color=col)
ax.axvline(5.5, color="black", linestyle="--", linewidth=1)
ax.text(2.5, ax.get_ylim()[1]*0.93, "SPEC CPU2017", ha="center", fontweight="bold")
ax.text(8.5, ax.get_ylim()[1]*0.93, "Google Datacenter (gtrace_v2)", ha="center", fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(short_names, rotation=25, ha="right")
ax.set_ylabel("LLC Hit Rate (%)")
ax.set_title("2MB 16-Way LLC Hit Rate Across SPEC17 and Google Datacenter Workloads")
ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("results/plots_cp2/fig1_hitrate_2mb.png", dpi=200)
plt.close()

# Plot 2: Normalized IPC vs LRU (2MB)
fig, ax = plt.subplots(figsize=(13, 5))
for i, (pol, lbl, col) in enumerate(zip(policies, labels, colors)):
    vals = []
    for t in traces_12:
        if (pol, "2mb", t) in data and ("lru", "2mb", t) in data:
            vals.append(data[(pol, "2mb", t)]["ipc"] / data[("lru", "2mb", t)]["ipc"])
        else:
            vals.append(1.0)
    ax.bar(x + (i - 2.5) * w, vals, width=w, label=lbl, color=col)
ax.axhline(1.0, color="gray", linestyle=":", linewidth=1)
ax.axvline(5.5, color="black", linestyle="--", linewidth=1)
ax.set_xticks(x)
ax.set_xticklabels(short_names, rotation=25, ha="right")
ax.set_ylabel("Normalized IPC (vs. LRU)")
ax.set_title("Normalized IPC Across SPEC17 and Google Datacenter Workloads (2MB LLC)")
ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("results/plots_cp2/fig2_norm_ipc_2mb.png", dpi=200)
plt.close()

# Plot 3: LLC MPKI (2MB)
fig, ax = plt.subplots(figsize=(13, 5))
for i, (pol, lbl, col) in enumerate(zip(policies, labels, colors)):
    vals = [data[(pol, "2mb", t)]["mpki"] if (pol, "2mb", t) in data else 0 for t in traces_12]
    ax.bar(x + (i - 2.5) * w, vals, width=w, label=lbl, color=col)
ax.axvline(5.5, color="black", linestyle="--", linewidth=1)
ax.set_xticks(x)
ax.set_xticklabels(short_names, rotation=25, ha="right")
ax.set_ylabel("LLC MPKI")
ax.set_title("LLC Misses Per Kilo-Instruction (MPKI) at 2MB Capacity")
ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("results/plots_cp2/fig3_mpki_2mb.png", dpi=200)
plt.close()

# Plot 4: 2MB -> 4MB -> 8MB -> 16MB Capacity Sweep
sweep_4 = [l.strip().split("/")[-1].split(".")[0] for l in open("traces_4_sweep.txt") if l.strip()]
sizes = ["2mb", "4mb", "8mb", "16mb"]
size_labels = ["2 MB", "4 MB", "8 MB", "16 MB"]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for idx, (ax, t) in enumerate(zip(axes.flat, sweep_4)):
    for pol, lbl, col in zip(policies, labels, colors):
        hrs = [data[(pol, sz, t)]["hit_rate"] if (pol, sz, t) in data else 0 for sz in sizes]
        ax.plot(size_labels, hrs, marker="o", label=lbl, color=col, linewidth=2)
    ax.set_title(t.split("-")[0].replace("_0000", ""))
    ax.set_ylabel("LLC Hit Rate (%)")
    ax.grid(True, alpha=0.3)
    if idx == 0:
        ax.legend(ncol=2, fontsize=8)
plt.suptitle("LLC Capacity Sensitivity Sweep (2MB to 16MB)", fontweight="bold")
plt.tight_layout()
plt.savefig("results/plots_cp2/fig4_capacity_sweep.png", dpi=200)
plt.close()

print("\n=== SUMMARY (2MB) ===")
for pol, lbl in zip(policies, labels):
    spec_hr = np.mean([data[(pol, "2mb", t)]["hit_rate"] for t in traces_12[:6] if (pol, "2mb", t) in data])
    goog_hr = np.mean([data[(pol, "2mb", t)]["hit_rate"] for t in traces_12[6:] if (pol, "2mb", t) in data])
    spec_ipc = np.exp(np.mean(np.log([data[(pol, "2mb", t)]["ipc"] for t in traces_12[:6] if (pol, "2mb", t) in data])))
    goog_ipc = np.exp(np.mean(np.log([data[(pol, "2mb", t)]["ipc"] for t in traces_12[6:] if (pol, "2mb", t) in data])))
    print(f"{lbl:12s} | SPEC Avg Hit%: {spec_hr:5.2f}%  Geomean IPC: {spec_ipc:.4f} | Google Avg Hit%: {goog_hr:5.2f}%  Geomean IPC: {goog_ipc:.4f}")
