# CS683 Project: Last Level Cache Replacement Policies on Datacenter Workloads

**Name:** Swapnil Bakoliya (Roll No: 26M1150)  
**Course:** CS683 Advanced Computer Architecture, IIT Bombay  

## 1. Overview
Most cache replacement policies are evaluated on SPEC CPU workloads, which usually have regular loops and predictable reuse. Datacenter workloads behave very differently and tend to have much larger code and data footprints.

In this project, I compare 6 LLC replacement policies in ChampSim across 6 SPEC CPU2017 traces and 6 Google DPC-4 (`gtrace_v2`) datacenter traces, along with a cache size sweep from 2MB to 16MB.

## 2. Experimental Setup (Checkpoint 2)
All simulations run on a 1-core out-of-order ChampSim model with hardware prefetchers turned off to isolate replacement policy behavior.

| Parameter | Configuration |
| :--- | :--- |
| **Core** | 1-core OoO, 4-wide issue, 128-entry ROB |
| **L1I / L1D** | 32 KB, 8-way, 4-cycle hit latency |
| **L2 Cache** | 256 KB, 8-way, 12-cycle hit latency |
| **Baseline LLC** | 2 MB, 16-way, 20-cycle hit latency (2048 sets, 64B blocks), 64 MSHRs |
| **Capacity Sweep** | 2 MB, 4 MB, 8 MB, and 16 MB (on 4 traces) |
| **Prefetchers** | None (disabled at all levels) |
| **Simulation Window** | 10M warmup instructions + 10M simulation instructions (144 total runs) |

### Workloads Selected (All Baseline LLC MPKI > 1.0)
* **SPEC CPU2017 (6 traces):** `602.gcc_s`, `605.mcf_s`, `620.omnetpp_s`, `623.xalancbmk_s`, `649.fotonik3d_s`, `654.roms_s`
* **Google DPC-4 `gtrace_v2` (6 traces):** `arizona_0000`, `charlie_0000`, `delta_0000`, `merced_0000`, `tahoe_0000`, `yankee_0000`

## 3. Policies Evaluated
1. **LRU:** ChampSim baseline recency replacement.
2. **SRRIP:** ChampSim baseline 2-bit RRIP (`maxRRPV = 3`, inserts at `2`).
3. **DRRIP:** ChampSim baseline set-dueling between SRRIP and BRRIP.
4. **SHiP:** ChampSim baseline PC-indexed SHCT predictor.
5. **Hawkeye (`replacement/hawkeye/`):** Custom C++ implementation using 64 sampled sets with a 128-entry `OPTgen` and a 4096-entry PC `SHCT` (inserts friendly fills at `RRPV = 0` and averse fills at `7`).
6. **Mockingjay (`replacement/mockingjay/`):** Custom C++ implementation using 64 sampled sets to track reuse distance into a 4096-entry PC `RDP`, aging `ETR` on set accesses and evicting expired lines (`ETR < -4`) first.

## 4. Checkpoint 2 Results (2MB Baseline)

| Policy | SPEC Avg Hit Rate | SPEC Geomean IPC | Google Avg Hit Rate | Google Geomean IPC |
| :--- | :---: | :---: | :---: | :---: |
| **LRU** | 31.08% | 0.3461 | **39.19%** | **0.5063** |
| **SRRIP** | 30.92% | **0.4197** | 17.96% | 0.4924 |
| **DRRIP** | **43.39%** | 0.4034 | 33.51% | 0.5021 |
| **SHiP** | 43.22% | 0.4143 | 38.14% | 0.5048 |
| **Hawkeye** | 34.60% | 0.3570 | 38.59% | 0.5049 |
| **Mockingjay** | 42.80% | 0.4145 | 27.19% | 0.4908 |

### Main Observations & Setup Limits
* **SPEC vs Google flip:** DRRIP (43.4%), SHiP (43.2%), and Mockingjay (42.8%) beat LRU (31.1%) on SPEC, mainly because `605.mcf_s` jumps from 26.0% to >72% and `623.xalancbmk_s` jumps from 36.8% to >84%. On Google traces, plain LRU gets the highest average hit rate (39.2%) and beats all 5 other policies.
* **Google trace regressions:** SRRIP drops to 5.2% hit rate on `charlie_0000` (LRU is 47.7%), and Mockingjay averages 27.2% across Google traces. Only SHiP beats LRU hit rate on `delta_0000`, `tahoe_0000`, and `merced_0000`.
* **Hit rate vs IPC:** On `649.fotonik3d_s`, SRRIP drops hit rate from 53.5% to 6.9%, yet normalized IPC stays close to 1.0. Across Google traces, geomean IPC stays nearly flat around 0.49 to 0.51 for all policies.
* **Capacity sweep (2MB to 16MB):** On `605.mcf_s`, LRU jumps from 26.0% at 2MB to 93.3% at 4MB and flattens around 96.8% at 8MB. `602.gcc_s` stays below 0.25% hit rate even at 16MB. `tahoe_0000` keeps scaling up to 67.4% at 16MB under LRU (SRRIP stays at 58.2%).
* **16MB warmup limit:** 10M warmup instructions is too short to fill a 16MB cache (262k lines). On `arizona_0000`, there are only ~65k LLC accesses total, so the cache never fills up and all policies tie at 22,286 hits by 8MB–16MB.

## 5. Repository Structure
* `replacement/hawkeye/`: C++ implementation of Hawkeye for ChampSim
* `replacement/mockingjay/`: C++ implementation of Mockingjay for ChampSim
* `configs/`: ChampSim JSON config files for 2MB, 4MB, 8MB, and 16MB sweeps
* `results/cp2_results.csv`: Parsed IPC, hit rate, and MPKI across all 144 runs
* `results/plots_cp2/`: Generated figures (`fig1_hitrate_2mb.png`, `fig2_norm_ipc_2mb.png`, `fig3_mpki_2mb.png`, `fig4_capacity_sweep.png`)
* `scripts/parse_and_plot_cp2.py`: Script used to parse simulation logs and generate plots
* `traces_12.txt`: List of the 12 traces used in Checkpoint 2
