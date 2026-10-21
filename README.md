# CS683 Project: LLC Replacement Policies on Datacenter Workloads

**Author:** Swapnil Bakoliya (Roll: 26M1150)  
**Course:** CS683 Advanced Computer Architecture, IIT Bombay  

---

## 1. Overview
Most cache replacement policies (such as SRRIP and DRRIP) were evaluated on SPEC CPU benchmarks, where memory access patterns are dominated by loops or sequential scans. Datacenter software (RPC services, search queries, distributed storage) features larger code footprints, deep call stacks, and irregular pointer traversals.

This project evaluates how standard LLC replacement policies behave on real Google datacenter traces from DPC-4 (HPCA 2026) compared against SPEC CPU 2017 baselines in ChampSim.

---

## 2. Experimental Setup

Simulations run on ChampSim in a single-core out-of-order configuration with hardware prefetchers disabled to isolate replacement decisions.

| Parameter | Value |
| :--- | :--- |
| Core | 1-core OoO, 4-wide fetch/retire, 128-entry ROB |
| L1 D-Cache / I-Cache | 32 KB, 8-way, 4 cycles |
| L2 Cache | 256 KB, 8-way, 12 cycles |
| LLC | 2 MB, 16-way, 20 cycles (2048 sets, 64B lines) |
| Prefetcher | None |
| Simulation Window | 2M warmup, 10M detailed execution |

**Workloads:**
* `SPEC: 602.gcc_s` (SPEC CPU 2017): Reference desktop benchmark (17.83 LLC MPKI).
* `Google: arizona_0000` (DPC-4 gtrace_v2): Production datacenter trace (3.34 LLC MPKI).

---

## 3. Checkpoint-1 Results

| Workload | Policy | IPC | LLC Hits | LLC Misses | Hit Rate | LLC MPKI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SPEC: 602.gcc_s` | LRU | 0.2886 | 351 | 178,289 | 0.20% | 17.83 |
| `SPEC: 602.gcc_s` | SRRIP | 0.2890 | 96 | 178,544 | 0.05% | 17.85 |
| `SPEC: 602.gcc_s` | DRRIP | 0.2888 | 343 | 178,297 | 0.19% | 17.83 |
| `Google: arizona_0000` | LRU | 0.9461 | 15,183 | 33,353 | 31.28% | 3.34 |
| `Google: arizona_0000` | SRRIP | 0.9484 | 13,844 | 34,706 | 28.51% | 3.47 |
| `Google: arizona_0000` | DRRIP | 0.9461 | 15,015 | 33,521 | 30.94% | 3.35 |

### Observations
1. **SRRIP hit degradation on Google trace:** On `arizona_0000`, SRRIP drops hit rate from 31.28% to 28.51% (-1,339 hits compared to LRU). Inserting lines with distant RRPV ($RRPV = 2^M - 2$) evicts useful blocks too early due to irregular reuse intervals.
2. **DRRIP Set-Dueling back to LRU:** Monitor sets detect that SRRIP causes more misses than bimodal insertion. The PSEL counter saturates toward bimodal/LRU insertion, recovering the hit rate to 30.94% and matching LRU's 0.9461 IPC.

---

## 4. Repository Structure

* `configs/`: ChampSim configuration files (2MB LLC, prefetcher disabled).
* `results/raw_dumps/`: Raw ChampSim output logs.
* `results/plots/`: Comparison plots (IPC, Hit Rate, MPKI).
* `results/summary.csv`: Parsed metrics table.
* `scripts/`: Log parser (`parse_results.py`), plotting (`plot_results.py`), and locality profiler (`profile_locality.py`).
* `traces/`: Trace index and metadata (`manifest.txt`).

---

## 5. Next Steps (Checkpoint-2)
* Evaluate PC-signature and predictor policies: SHiP, Hawkeye, and Mockingjay.
* Sweep LLC size (2 MB to 16 MB) to observe capacity sensitivity.
