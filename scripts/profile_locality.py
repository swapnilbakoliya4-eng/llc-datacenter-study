#!/usr/bin/env python3
import sys
import argparse
from collections import defaultdict

def profile_stream(stream_iter, llc_capacity_blocks=32768):
    unique_lines = set()
    last_seen = {}
    reuse_distances = []
    pc_stats = defaultdict(lambda: {"hits": 0, "total": 0})

    for access_idx, (pc, addr) in enumerate(stream_iter):
        line_addr = addr >> 6
        unique_lines.add(line_addr)

        if line_addr in last_seen:
            dist = access_idx - last_seen[line_addr]
            reuse_distances.append(dist)
            in_cache = dist <= llc_capacity_blocks
            pc_stats[pc]["hits"] += 1 if in_cache else 0
        pc_stats[pc]["total"] += 1
        last_seen[line_addr] = access_idx

    total_accesses = sum(d["total"] for d in pc_stats.values())
    footprint_bytes = len(unique_lines) * 64
    footprint_mb = footprint_bytes / (1024 * 1024)
    llc_mb = (llc_capacity_blocks * 64) / (1024 * 1024)

    consistencies = []
    for pc, data in pc_stats.items():
        if data["total"] >= 5:
            p = data["hits"] / float(data["total"])
            consistencies.append(abs(p - 0.5) * 2.0)

    avg_consistency = (sum(consistencies) / len(consistencies)) if consistencies else 0.0

    if reuse_distances:
        sorted_dist = sorted(reuse_distances)
        n = len(sorted_dist)
        p50 = sorted_dist[int(0.50 * n)]
        p90 = sorted_dist[int(0.90 * n)]
        p99 = sorted_dist[int(0.99 * n)]
    else:
        p50, p90, p99 = 0, 0, 0

    print("=" * 60)
    print("Workload Locality Profile (Policy-Independent)")
    print("=" * 60)
    print(f"Total Accesses Evaluated : {total_accesses:,}")
    print(f"Unique 64B Cache Lines   : {len(unique_lines):,}")
    print(f"Working Set Footprint    : {footprint_mb:.2f} MB ({footprint_mb / llc_mb:.2f}x of {llc_mb:.1f} MB LLC)")
    print(f"Tracked Instructions (PC): {len(pc_stats):,}")
    print(f"Mean PC Consistency      : {avg_consistency:.3f}  [0.0 = random noise, 1.0 = pure]")
    print("-" * 60)
    print("Reuse Distance Distribution (in accesses):")
    print(f"  Median (p50)           : {p50:,}")
    print(f"  90th percentile (p90)  : {p90:,}")
    print(f"  99th percentile (p99)  : {p99:,}")
    print("=" * 60)

def generate_synthetic_stream():
    # Synthetic verification stream: 40k memory accesses
    # Mixes tight loop PCs (high consistency) with streaming PCs (low consistency)
    import random
    random.seed(42)
    stream = []
    for _ in range(2000):
        # Hot loop (PC 0x400100) touches 128 lines repeatedly
        for offset in range(16):
            stream.append((0x400100, 0x10000000 + (offset << 6)))
        # Irregular streaming accesses (PC 0x400200)
        for _ in range(4):
            addr = 0x20000000 + (random.randint(0, 100000) << 6)
            stream.append((0x400200, addr))
    return stream

def parse_text_stream(filepath):
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                yield int(parts[0], 16), int(parts[1], 16)

def main():
    parser = argparse.ArgumentParser(description="Policy-independent LLC access stream profiler")
    parser.add_argument("access_file", nargs="?", help="Path to whitespace-delimited text access stream (PC ADDR)")
    parser.add_argument("--demo", action="store_true", help="Run on synthetic mixed access stream for pipeline validation")
    parser.add_argument("--llc-blocks", type=int, default=32768, help="LLC capacity in 64B blocks (default: 32768 = 2MB)")
    args = parser.parse_args()

    if args.demo or not args.access_file:
        print("[*] Running synthetic validation stream...")
        stream = generate_synthetic_stream()
        profile_stream(stream, args.llc_blocks)
    else:
        stream = parse_text_stream(args.access_file)
        profile_stream(stream, args.llc_blocks)

if __name__ == "__main__":
    main()
