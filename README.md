# CS683 Project: LLC Replacement Policies on Datacenter Workloads

**Name:** Swapnil Bakoliya (Roll: 26M1150)  
**Course:** CS683 Advanced Computer Architecture, IIT Bombay  

## 1. Overview
Cache replacement policies like Static and Dynamic Re-Reference Interval Prediction (SRRIP and DRRIP) were originally tested on SPEC benchmarks. SPEC programs mostly consist of loops and sequential scans. 

Datacenter software (such as RPC handlers, web search, and distributed storage) behaves differently. It has large code footprints, deep call stacks, and irregular pointer-chasing memory accesses. 

This project evaluates how standard Last-Level Cache (LLC) replacement policies perform on Google datacenter traces from DPC-4 compared to SPEC CPU 2017 in ChampSim.

## 2. Experimental Setup (Checkpoint-1)
Simulations run on ChampSim using a single-core out-of-order model. Hardware prefetchers are disabled to observe pure cache replacement decisions.

| Parameter | Value |
| :--- | :--- |
| Core | 1-core OoO, 4-wide fetch/retire, 128-entry ROB |
| L1 D-Cache / I-Cache | 32 KB, 8-way, 4 cycles |
| L2 Cache | 256 KB, 8-way, 12 cycles |
| Last-Level Cache (LLC) | 2 MB, 16-way, 20 cycles (2048 sets, 64B lines) |
| Prefetcher | None (disabled) |
| Simulation Window | 2M warmup, 10M detailed execution |

Workloads used for Checkpoint-1 (screened for LLC Misses Per Kilo-Instruction > 1.0):
* SPEC: `602.gcc_s` (17.83 LLC MPKI)
* Google: `arizona_0000` (3.34 LLC MPKI)

## 3. Checkpoint-1 Results

| Workload | Policy | IPC | LLC Hits | LLC Misses | Hit Rate | LLC MPKI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SPEC: 602.gcc_s | LRU | 0.2886 | 351 | 178,289 | 0.20% | 17.83 |
| SPEC: 602.gcc_s | SRRIP | 0.2890 | 96 | 178,544 | 0.05% | 17.85 |
| SPEC: 602.gcc_s | DRRIP | 0.2888 | 343 | 178,297 | 0.19% | 17.83 |
| SPEC: 602.gcc_s | SHIP | 0.2907 | 254 | 178,386 | 0.14% | 17.84 |
| Google: arizona_0000 | LRU | 0.9461 | 15,183 | 33,353 | 31.28% | 3.34 |
| Google: arizona_0000 | SRRIP | 0.9484 | 13,844 | 34,706 | 28.51% | 3.47 |
| Google: arizona_0000 | DRRIP | 0.9461 | 15,015 | 33,521 | 30.94% | 3.35 |
| Google: arizona_0000 | SHIP | 0.9485 | 15,178 | 33,368 | 31.27% | 3.34 |

### Observations
1. **SRRIP hit rate drops on Google datacenter trace:** On `arizona_0000`, SRRIP drops hit rate from 31.28% to 28.51% (-1,339 hits compared to LRU). Datacenter accesses have irregular, spread-out reuse intervals. Inserting lines with distant RRPV evicts useful lines too early.
2. **DRRIP sets duel back to LRU:** Monitor sets detect that SRRIP causes more misses than bimodal insertion. The PSEL counter shifts follower sets to bimodal/LRU insertion, recovering the hit rate to 30.94%.
3. **SHiP uses PC signatures:** SHiP indexes the SHCT table using the load instruction PC. It identifies lines that actually get reused and avoids evicting them early, matching LRU hit rate at 31.27% and giving the highest IPC (0.9485).

## 4. Repository Structure
* `configs/`: ChampSim configuration files (2MB LLC, prefetcher disabled)
* `results/raw_dumps/`: Raw simulation output logs
* `results/plots/`: Comparison plots (`ipc_comparison.png`, `hit_rate_mpki.png`)
* `results/summary.csv`: Parsed metrics table
* `scripts/`: Log parser (`parse_results.py`), plotting (`plot_results.py`), and locality profiler (`profile_locality.py`)
* `traces/`: Trace index and metadata (`manifest.txt`)

## 5. Checkpoint-2 Plan
1. **Port Hawkeye:** Implement the OPTgen predictor and 2K-entry PC table in ChampSim C++ classes.
2. **Port Mockingjay:** Implement reuse distance prediction and Estimated Time of Arrival (ETA) eviction.
3. **LLC Capacity Sweep:** Test 2MB, 4MB, 8MB, and 16MB LLC sizes to find working set knees.
4. **Expand Traces:** Run 6 Google datacenter traces and 6 SPEC CPU 2017 traces at 50M to 100M instructions.
5. **Locality Profiling:** Profile reuse distance CDFs and PC hit consistency across workloads using `profile_locality.py`.
