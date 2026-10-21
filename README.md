# LLC Replacement Policies on Datacenter Workloads: A Characterization Study

**Course:** CS683 Advanced Computer Architecture  
**Author:** Swapnil Bakoliya (Roll: 26m1150), IIT Bombay  

---

## 1. Overview
Cache replacement policies like SRRIP and DRRIP were historically designed around scientific and desktop benchmarks (SPEC CPU), where execution is dominated by tight loops and high temporal locality. Warehouse-scale datacenter software (e.g., Google microservices, RPC frameworks, search indexing) exhibits fundamentally different memory behavior, featuring deep call stacks, large instruction working sets, and irregular pointer-chasing.

This project investigates where and why classical and predictive Last-Level Cache (LLC) replacement policies fail on hyperscale datacenter traces from **DPC-4 (HPCA 2026)** compared to SPEC CPU 2017 baselines.

---

## 2. Experimental Configuration

Simulations use ChampSim configured for single-core execution with all hardware prefetchers disabled to strictly isolate replacement decisions.

| Parameter | Configuration |
| :--- | :--- |
| **Core Model** | 1-core out-of-order, 4-wide fetch/decode/retire, 128-entry ROB |
| **L1 Data / Instruction** | 32 KB, 8-way set-associative, 4-cycle latency |
| **L2 Cache** | 256 KB, 8-way set-associative, 12-cycle latency |
| **Last-Level Cache (LLC)** | **2 MB, 16-way set-associative, 20-cycle latency** (2,048 sets, 64B line) |
| **Prefetcher** | None (disabled) |
| **Evaluation Window** | 2,000,000 warmup instructions, 10,000,000 simulation instructions |

**Workloads Evaluated:**
* `SPEC: 602.gcc_s` (SPEC CPU 2017): Reference desktop benchmark (17.83 LLC MPKI).
* `Google: arizona_0000` (DPC-4 gtrace_v2): Production datacenter service trace (3.34 LLC MPKI).

---

## 3. Checkpoint-1 Baseline Results

| Workload | Policy | IPC | LLC Hits | LLC Misses | Hit Rate | LLC MPKI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SPEC: 602.gcc_s` | LRU | 0.2886 | 351 | 178,289 | 0.20% | 17.83 |
| `SPEC: 602.gcc_s` | SRRIP | 0.2890 | 96 | 178,544 | 0.05% | 17.85 |
| `SPEC: 602.gcc_s` | DRRIP | 0.2888 | 343 | 178,297 | 0.19% | 17.83 |
| `Google: arizona_0000` | LRU | 0.9461 | 15,183 | 33,353 | 31.28% | 3.34 |
| `Google: arizona_0000` | SRRIP | 0.9484 | 13,844 | 34,706 | 28.51% | 3.47 |
| `Google: arizona_0000` | DRRIP | 0.9461 | 15,015 | 33,521 | 30.94% | 3.35 |

**Key Findings:**
1. **SRRIP Degradation on Datacenter Workload:** On `arizona_0000`, static SRRIP loses 1,339 cache hits compared to LRU, dropping hit rate from 31.28% to 28.51%. Datacenter memory references exhibit heavy-tailed, irregular reuse intervals. Inserting lines with distant RRPV (`RRPV = 2^M - 2`) causes useful lines to age out before their second reference.
2. **DRRIP Set-Dueling Saturation:** DRRIP dedicated monitor sets detect that SRRIP causes higher miss counts than bimodal insertion. The Policy Selection Counter (PSEL) dynamically steers follower sets back toward bimodal/LRU insertion, recovering hit rate to 30.94% and resulting in identical IPC (0.9461).

---

## 4. Repository Structure

* `configs/`: ChampSim configuration files (2MB LLC, prefetcher OFF).
* `results/raw_dumps/`: Raw simulation output logs.
* `results/plots/`: Comparative metric plots (IPC, Hit Rate, MPKI).
* `results/summary.csv`: Parsed metric summary.
* `scripts/`: Log parser (`parse_results.py`), plotting (`plot_results.py`), and locality profiler (`profile_locality.py`).
* `traces/`: DPC-4 trace manifest and download metadata.

---

## 5. Checkpoint-2 Roadmap (Phase 2 Target: Nov 26)
* **Predictive Policy Evaluation:** Port and evaluate fine-grained signature-based predictors: SHiP (PC signatures), Hawkeye (OPTgen / Belady MIN classifier), and Mockingjay (continuous ETA reuse distance).
* **Footprint Scaling:** Sweep LLC capacity from 2 MB to 16 MB to identify the threshold where datacenter workloads transition from capacity thrashing to stability.\n