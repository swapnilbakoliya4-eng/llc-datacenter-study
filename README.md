# CS683 Project: LLC Replacement Policies on Datacenter Workloads

**Author:** Swapnil Bakoliya (Roll: 26M1150)  
**Course:** CS683 Advanced Computer Architecture, IIT Bombay  

---

## 1. Overview
Most cache replacement policies (such as SRRIP and DRRIP) were originally proposed and evaluated on SPEC CPU benchmarks, where access patterns are heavily driven by loops and sequential arrays. Production datacenter software (microservices, RPC handling, search indexing) runs over massive code footprints with deep call stacks, frequent pointer chasing, and low instruction-cache reuse.

This project investigates where and why classical and predictive LLC replacement policies break on real Google datacenter traces from DPC-4 (HPCA 2026) compared against memory-intensive SPEC CPU 2017 baselines in ChampSim.

---

## 2. Experimental Setup (Checkpoint-1)

Simulations are configured on ChampSim using a single-core out-of-order model with hardware prefetchers disabled to strictly isolate cache replacement behavior.

| Parameter | Configuration |
| :--- | :--- |
| Core | 1-core OoO, 4-wide fetch/decode/retire, 128-entry ROB |
| L1 D-Cache / I-Cache | 32 KB, 8-way, 4 cycles |
| L2 Cache | 256 KB, 8-way, 12 cycles |
| Last-Level Cache (LLC) | 2 MB, 16-way, 20 cycles (2048 sets, 64B line) |
| Prefetcher | Disabled (none) |
| Simulation Window | 2,000,000 warmup, 10,000,000 detailed execution |

**Workloads Screened for Checkpoint-1:**
* `SPEC: 602.gcc_s` (SPEC CPU 2017): Reference compute/control-flow benchmark (17.83 LLC MPKI).
* `Google: arizona_0000` (DPC-4 gtrace_v2): Production datacenter service trace (3.34 LLC MPKI).

---

## 3. Checkpoint-1 Results

| Workload | Policy | IPC | LLC Hits | LLC Misses | Hit Rate | LLC MPKI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SPEC: 602.gcc_s` | LRU | 0.2886 | 351 | 178,289 | 0.20% | 17.83 |
| `SPEC: 602.gcc_s` | SRRIP | 0.2890 | 96 | 178,544 | 0.05% | 17.85 |
| `SPEC: 602.gcc_s` | DRRIP | 0.2888 | 343 | 178,297 | 0.19% | 17.83 |
| `SPEC: 602.gcc_s` | SHIP | 0.2907 | 254 | 178,386 | 0.14% | 17.84 |
| `Google: arizona_0000` | LRU | 0.9461 | 15,183 | 33,353 | 31.28% | 3.34 |
| `Google: arizona_0000` | SRRIP | 0.9484 | 13,844 | 34,706 | 28.51% | 3.47 |
| `Google: arizona_0000` | DRRIP | 0.9461 | 15,015 | 33,521 | 30.94% | 3.35 |
| `Google: arizona_0000` | SHIP | 0.9485 | 15,178 | 33,368 | 31.27% | 3.34 |

### Observations
1. **SRRIP Hit Rate Collapse on Datacenter Workload:** On `arizona_0000`, static SRRIP loses 1,339 cache hits compared to LRU, dropping hit rate from 31.28% to 28.51%. Datacenter memory references exhibit heavy-tailed, irregular reuse intervals. Inserting lines with distant RRPV ($RRPV = 2^M - 2$) causes useful lines to age out before their second reference.
2. **DRRIP Set-Dueling Retreat to LRU:** Dedicated monitor sets detect that SRRIP causes higher miss counts than bimodal insertion. The Policy Selection Counter (PSEL) steers follower sets back toward bimodal/LRU insertion, recovering hit rate to 30.94% and resulting in identical IPC (0.9461).
3. **SHiP Signature Filtering:** By tracking load instruction PCs via the Signature History Counter Table (SHCT), SHiP avoids penalizing reusable lines with distant RRPV. It recovers the full hit count (15,178 hits) and achieves the highest IPC (0.9485).

---

## 4. Repository Structure

* `configs/`: ChampSim configuration files (2MB LLC, prefetcher disabled).
* `results/raw_dumps/`: Raw simulation output logs.
* `results/plots/`: Calibrated comparative plots (`ipc_comparison.png`, `hit_rate_mpki.png`).
* `results/summary.csv`: Parsed metrics table.
* `scripts/`: Log parser (`parse_results.py`), plotting (`plot_results.py`), and locality profiler (`profile_locality.py`).
* `traces/`: Trace index and metadata (`manifest.txt`).

---

## 5. Checkpoint-2 Work Plan & Next Steps

Checkpoint-1 validated the simulation harness, established baseline performance across 4 policies, and proved that coarse RRPV aging degrades under datacenter traffic. The remaining work for the final milestone includes:

1. **Porting Predictive & ML-Based Policies:**
   * Adapt **Hawkeye** (ISCA 2016) from CRC-2 legacy code into modern ChampSim C++17 class modules, integrating Bélády-based OPTgen sampled training with a 2K-entry PC predictor table.
   * Port **Mockingjay** (MICRO 2022) to evaluate fine-grained reuse distance prediction and Estimated Time of Arrival (ETA) eviction against Hawkeye and SHiP.

2. **Scaling the Workload Evaluation Matrix:**
   * Expand from pilot traces to a full 12–14 trace matrix:
     * 6–8 distinct Google DPC-4 datacenter traces screened for LLC MPKI > 1.0.
     * 6 reference SPEC CPU 2017 memory-intensive traces (`mcf`, `lbm`, `omnetpp`, `gcc`, `bwaves`, `cam4`).
   * Increase simulation duration from 10M to 50M–100M instructions to capture steady-state phase transitions.

3. **Cache Capacity Sensitivity Sweeps:**
   * Sweep LLC capacity across 2 MB, 4 MB, 8 MB, and 16 MB to identify the working-set inflection point where each policy transitions from thrashing to stability.

4. **Workload Property Correlation:**
   * Use `profile_locality.py` to extract reuse distance CDFs, working-set footprint ratios, and per-PC reuse consistency across all workloads, correlating performance gains/losses directly to access stream characteristics.

5. **Prefetcher Interaction Study (Time Permitting):**
   * Re-evaluate the best-performing policies with standard L2 prefetchers enabled (Next-Line, IP-Stride) to measure whether hardware prefetching masks or interferes with replacement decisions.
