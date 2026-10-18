#!/usr/bin/env python3
import sys, os, re, csv

log_dir = sys.argv[1] if len(sys.argv) > 1 else "results/checkpoint1_logs"
results = []

if not os.path.exists(log_dir):
    print(f"Log directory '{log_dir}' not found.")
    sys.exit(0)

for fname in sorted(os.listdir(log_dir)):
    if not fname.endswith(".log"):
        continue
    filepath = os.path.join(log_dir, fname)
    trace_tag = fname.replace(".log", "")
    
    ipc, llc_miss, total_inst = None, None, None
    with open(filepath, "r") as f:
        for line in f:
            if "cumulative IPC" in line:
                m = re.search(r"cumulative IPC:\s*([0-9.]+)", line)
                if m: ipc = float(m.group(1))
            elif "LLC TOTAL" in line and "MISS:" in line:
                m = re.search(r"MISS:\s*([0-9]+)", line)
                if m: llc_miss = int(m.group(1))
            elif "cumulative instructions:" in line:
                m = re.search(r"instructions:\s*([0-9]+)", line)
                if m: total_inst = int(m.group(1))
                
    mpki = (llc_miss / (total_inst / 1000.0)) if (llc_miss and total_inst) else 0.0
    results.append({"Run": trace_tag, "IPC": ipc, "LLC_MPKI": round(mpki, 3)})

if results:
    print(f"{'Run / Configuration':<30} | {'IPC':<8} | {'LLC MPKI':<8}")
    print("-" * 52)
    for r in results:
        print(f"{r['Run']:<30} | {str(r['IPC']):<8} | {str(r['LLC_MPKI']):<8}")
