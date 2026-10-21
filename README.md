\### LLC Replacement Policies on Datacenter Workloads: A Characterization Study



\*\*Course:\*\* CS683 Advanced Computer Architecture  

\*\*Author:\*\* Swapnil Bakoliya (Roll: 26m1150), IIT Bombay  



\---



\#### 1. Overview

Cache replacement policies like SRRIP and DRRIP were historically designed around scientific and desktop benchmarks (SPEC CPU), where execution is dominated by tight loops and high temporal locality. Warehouse-scale datacenter software (e.g., Google microservices, RPC frameworks, search indexing) exhibits fundamentally different memory behavior, featuring deep call stacks, large instruction working sets, and irregular pointer-chasing.



This project investigates where and why classical and predictive Last-Level Cache (LLC) replacement policies fail on hyperscale datacenter traces from \*\*DPC-4 (HPCA 2026)\*\* compared to SPEC CPU 2017 baselines.



\---



\#### 2. Checkpoint-1 Configuration



Simulations use ChampSim configured for single-core execution with all hardware prefetchers disabled to isolate replacement decisions.



| Parameter | Configuration |

| :--- | :--- |

| \*\*Core Model\*\* | 1-core out-of-order, 4-wide fetch/decode/retire, 128-entry ROB |

| \*\*L1 Data / Instruction\*\* | 32 KB, 8-way set-associative, 4-cycle latency |

| \*\*L2 Cache\*\* | 256 KB, 8-way set-associative, 12-cycle latency |

| \*\*Last-Level Cache (LLC)\*\* | \*\*2 MB, 16-way set-associative, 20-cycle latency\*\* (2,048 sets, 64B line) |

| \*\*Prefetcher\*\* | None (disabled) |

| \*\*Evaluation Window\*\* | 2,000,000 warmup instructions, 10,000,000 detailed simulation instructions |



\*\*Workloads Evaluated:\*\*

\* `SPEC: 602.gcc\_s` (SPEC CPU 2017): Reference desktop benchmark (17.83 LLC MPKI).

\* `Google: arizona\_0000` (DPC-4 `gtrace\_v2`): Production datacenter service trace (3.34 LLC MPKI).



\---



\#### 3. Checkpoint-1 Baseline Results



| Workload | Policy | Instructions | Cycles | IPC | LLC Hits | LLC Misses | Hit Rate (%) | LLC MPKI |

| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

| \*\*SPEC GCC\*\* | LRU | 10,000,001 | 34,648,322 | 0.2886 | 351 | 178,289 | 0.20% | 17.83 |

| (`602.gcc\_s`) | SRRIP | 10,000,001 | 34,600,905 | 0.2890 | 96 | 178,544 | 0.05% | 17.85 |

| | DRRIP | 10,000,001 | 34,624,322 | 0.2888 | 343 | 178,297 | 0.19% | 17.83 |

| \*\*Google DC\*\* | \*\*LRU\*\* | 10,000,002 | 10,569,230 | 0.9461 | \*\*15,183\*\* | 33,353 | \*\*31.28%\*\* | 3.34 |

| (`arizona\_0000`) | \*\*SRRIP\*\* | 10,000,002 | 10,543,860 | 0.9484 | \*\*13,844\*\* | 34,706 | \*\*28.51%\*\* | 3.47 |

| | \*\*DRRIP\*\* | 10,000,002 | 10,569,230 | 0.9461 | \*\*15,015\*\* | 33,521 | \*\*30.94%\*\* | 3.35 |



\*\*Key Findings:\*\*

1\. \*\*SRRIP Degradation on Datacenter Workload:\*\* On `arizona\_0000`, static SRRIP loses 1,339 cache hits compared to LRU, dropping hit rate from 31.28% to 28.51%. Datacenter memory references exhibit heavy-tailed, irregular reuse intervals. Inserting lines with distant RRPV ($RRPV = 2^M - 2$) causes useful lines to age out before their second reference.

2\. \*\*DRRIP Set-Dueling Saturation:\*\* DRRIP's dedicated monitor sets detect that SRRIP causes higher miss counts than bimodal insertion. The Policy Selection Counter (PSEL) dynamically steers follower sets back toward bimodal/LRU insertion, recovering hit rate to 30.94% and resulting in identical IPC (0.9461).



\---



\#### 4. Repository Structure



```text

├── configs/                # ChampSim configuration files (2MB LLC, prefetcher OFF)

│   ├── champsim\_base.json

│   ├── champsim\_srrip.json

│   └── champsim\_drrip.json

├── results/

│   ├── raw\_dumps/          # Raw simulation output logs

│   ├── plots/              # Comparative metric plots (IPC, Hit Rate, MPKI)

│   └── summary.csv         # Parsed metric summary

├── scripts/

│   ├── parse\_results.py    # Log parser extracting metrics to CSV

│   ├── plot\_results.py     # Generates comparative figures

│   └── profile\_locality.py # Policy-independent access stream profiler

└── traces/

&#x20;   └── manifest.txt        # DPC-4 trace manifest and download metadata

