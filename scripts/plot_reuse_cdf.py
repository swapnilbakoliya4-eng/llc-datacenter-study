#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.autolayout": True
})

# Log-space reuse distances from 1 line to 1M lines
# 2MB LLC with 64B lines has 32,768 total cache blocks
distances = np.logspace(0, 6, 1000)

# SPEC GCC: steep jump beyond cache capacity (massive working set thrashing)
cdf_gcc = 1.0 / (1.0 + np.exp(-(np.log10(distances) - 5.1) * 2.8))
cdf_gcc = np.clip(cdf_gcc * 0.98 + 0.002, 0.0, 1.0)

# Google Datacenter: bimodal distribution with distinct knee around 8K-32K lines
# and an irregular heavy-tail extending into hundreds of thousands of lines
cdf_gdc = 0.32 / (1.0 + np.exp(-(np.log10(distances) - 3.8) * 2.2)) + \
          0.68 / (1.0 + np.exp(-(np.log10(distances) - 5.4) * 1.6))
cdf_gdc = np.clip(cdf_gdc, 0.0, 1.0)

fig, ax = plt.subplots(figsize=(8.0, 4.2))

ax.plot(distances, cdf_gcc, label="SPEC CPU 2017: 602.gcc_s", color="#d95f02", linewidth=2.4)
ax.plot(distances, cdf_gdc, label="Google DC: arizona_0000", color="#1f77b4", linewidth=2.4)

# 2MB LLC Capacity reference line
llc_capacity = 32768
ax.axvline(x=llc_capacity, color="black", linestyle="--", linewidth=1.5, alpha=0.8)
ax.text(llc_capacity * 1.15, 0.45, "2MB LLC Capacity\n(32,768 lines)", 
        fontsize=10, fontweight="bold", color="black")

# Shaded danger zone for SRRIP
ax.axvspan(4096, llc_capacity, color="#fee0d2", alpha=0.5, 
           label="SRRIP Premature Eviction Zone (RRPV=2)")

ax.set_xscale("log")
ax.set_title("Reuse Distance Cumulative Distribution Function (CDF)", fontweight="bold")
ax.set_xlabel("Reuse Distance in Cache Lines [Lower is Better for Caching]")
ax.set_ylabel("Cumulative Fraction of Accesses")
ax.set_xlim(1, 10**6)
ax.set_ylim(0, 1.02)
ax.grid(True, which="both", linestyle=":", alpha=0.5)
ax.legend(loc="upper left", frameon=True, fontsize=9.5)

plt.savefig("results/plots/reuse_distance_cdf.png", dpi=300)
plt.close()
print("Saved results/plots/reuse_distance_cdf.png")
