# CS683 Project: Last Level Cache Replacement Policies on Datacenter Workloads

Name: Swapnil Bakoliya (Roll: 26M1150)
Course: CS683 Advanced Computer Architecture, IIT Bombay

## 1. Overview
Cache replacement policies such as Static Re-Reference Interval Prediction (SRRIP) and Dynamic Re-Reference Interval Prediction (DRRIP) target SPEC CPU benchmarks. SPEC benchmarks contain repetitive loops and regular array streaming.

Production datacenter software, including Remote Procedure Call (RPC) services, web search indexing, and distributed storage engines, exhibits different memory behavior. These services run across massive code footprints, execute deep call stacks, and produce irregular pointer chasing access patterns.

This project investigates where and why classical Last Level Cache (LLC) replacement policies fail on Google datacenter traces from the Fourth Data Prefetching Championship (DPC4) compared to memory intensive SPEC CPU 2017 baselines in ChampSim.

## 2. Experimental Setup (Checkpoint 1)
Simulations execute in ChampSim using a single core out of order model. Hardware prefetchers remain disabled to isolate pure cache replacement decisions.

| Parameter | Configuration Value |
|---|---|
| Core Engine | 1 core Out of Order (OoO), 4 wide fetch and retire, 128 entry Reorder Buffer (ROB) |
| L1 Data and Instruction Cache | 32 KB, 8 way, 4 cycles hit latency |
| L2 Cache | 256 KB, 8 way, 12 cycles hit latency |
| Last Level Cache (LLC) | 2 MB, 16 way, 20 cycles hit latency (2048 sets, 64B lines) |
| Prefetchers | None (all hardware prefetching disabled) |
| Simulation Window | 2,000,000 instructions warmup, 10,000,000 instructions detailed execution |

Workload selection enforces an LLC Misses Per Kilo Instruction (MPKI) threshold greater than 1.0:
1. SPEC CPU 2017: 602.gcc_s (17.83 LLC MPKI, compiler memory thrashing)
2. Google Datacenter: arizona_0000 (3.34 LLC MPKI, production microservice trace)

## 3. Checkpoint 1 Results

| Workload | Policy | Instructions Per Cycle (IPC) | LLC Hits | LLC Misses | Hit Rate (%) | LLC MPKI |
|---|---|---|---|---|---|---|
| SPEC: 602.gcc_s | LRU | 0.2886 | 351 | 178289 | 0.20% | 17.83 |
| SPEC: 602.gcc_s | SRRIP | 0.2890 | 96 | 178544 | 0.05% | 17.85 |
| SPEC: 602.gcc_s | DRRIP | 0.2888 | 343 | 178297 | 0.19% | 17.83 |
| SPEC: 602.gcc_s | SHIP | 0.2907 | 254 | 178386 | 0.14% | 17.84 |
| Google: arizona_0000 | LRU | 0.9461 | 15183 | 33353 | 31.28% | 3.34 |
| Google: arizona_0000 | SRRIP | 0.9484 | 13844 | 34706 | 28.51% | 3.47 |
| Google: arizona_0000 | DRRIP | 0.9461 | 15015 | 33521 | 30.94% | 3.35 |
| Google: arizona_0000 | SHIP | 0.9485 | 15178 | 33368 | 31.27% | 3.34 |

### Observations
1. SRRIP hit rate degrades on datacenter access streams: On arizona_0000, static SRRIP reduces hit rate from 31.28% to 28.51% (1339 fewer hits than LRU). Datacenter traffic features heavy tailed, irregular reuse intervals. Inserting blocks with distant Re-Reference Prediction Values (RRPV = 2) causes premature eviction before subsequent accesses occur.
2. DRRIP set dueling retreats to bimodal insertion: Monitor sets detect elevated misses under SRRIP. The Policy Selection Counter (PSEL) steers follower sets toward bimodal insertion, restoring hit rate to 30.94% and matching LRU performance.
3. SHiP preserves hit rate via program counter signatures: The Signature based Hit Predictor (SHiP) indexes the Signature History Counter Table (SHCT) using load instruction Program Counters. It filters dead lines while inserting reusable lines with low RRPV, achieving a 31.27% hit rate and 0.9485 IPC.

## 4. Repository Structure
1. configs/: ChampSim configuration files (2MB LLC, prefetchers disabled)
2. results/raw_dumps/: Raw simulation log outputs
3. results/plots/: Comparative evaluation figures (ipc_comparison.png, hit_rate_mpki.png)
4. results/summary.csv: Structured performance metrics table
5. scripts/: Automated log parser, figure generator, and locality profiler
6. traces/: Workload trace registry and index

## 5. Checkpoint 2 Work Plan
1. Port Hawkeye: Implement the OPTgen predictor and 2K entry table in ChampSim C++ classes.
2. Port Mockingjay: Implement reuse distance prediction and Estimated Time of Arrival eviction.
3. LLC Capacity Sweeps: Evaluate 2MB, 4MB, 8MB, and 16MB cache sizes.
4. Scale Workloads: Profile 6 Google datacenter traces and 6 SPEC CPU 2017 traces.
5. Locality Profiling: Extract reuse distance distributions using profile_locality.py.
