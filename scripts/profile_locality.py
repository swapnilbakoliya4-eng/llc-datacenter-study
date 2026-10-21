#!/usr/bin/env python3
import sys
import argparse
from collections import defaultdict

def profile(stream, llc_blocks=32768):
    lines = set()
    last_seen = {}
    rd = []
    pc_hits = defaultdict(lambda: [0, 0])

    for idx, (pc, addr) in enumerate(stream):
        blk = addr >> 6
        lines.add(blk)

        if blk in last_seen:
            d = idx - last_seen[blk]
            rd.append(d)
            if d <= llc_blocks:
                pc_hits[pc][0] += 1
        pc_hits[pc][1] += 1
        last_seen[blk] = idx

    footprint_mb = (len(lines) * 64) / (1024 * 1024)
    llc_mb = (llc_blocks * 64) / (1024 * 1024)

    scores = []
    for pc, (hits, total) in pc_hits.items():
        if total >= 5:
            p = hits / total
            scores.append(abs(p - 0.5) * 2.0)

    consistency = (sum(scores) / len(scores)) if scores else 0.0
    rd_sorted = sorted(rd) if rd else [0]
    n = len(rd_sorted)

    print(f"accesses: {sum(t for _, t in pc_hits.values())}")
    print(f"unique blocks: {len(lines)}")
    print(f"footprint: {footprint_mb:.2f} MB ({footprint_mb / llc_mb:.2f}x LLC)")
    print(f"mean pc consistency: {consistency:.3f}")
    print(f"reuse distance p50: {rd_sorted[int(0.50 * n)]}, p90: {rd_sorted[int(0.90 * n)]}")

def get_demo_stream():
    import random
    random.seed(42)
    s = []
    for _ in range(2000):
        for off in range(16):
            s.append((0x400100, 0x10000000 + (off << 6)))
        for _ in range(4):
            s.append((0x400200, 0x20000000 + (random.randint(0, 50000) << 6)))
    return s

def parse_file(path):
    with open(path) as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                yield int(p[0], 16), int(p[1], 16)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default=None)
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--llc-blocks", type=int, default=32768)
    args = parser.parse_args()

    if args.demo or not args.file:
        profile(get_demo_stream(), args.llc_blocks)
    else:
        profile(parse_file(args.file), args.llc_blocks)
