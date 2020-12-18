# SatFTA-v2.0

An SAT-based tool to compute minimal cut set (MCSs) in fault tree analysis (FTA).
The paper about this tool has been published in [1] and [2].

[1] Weilin Luo, Ou Wei, "WAP: SAT-Based Computation of Minimal Cut Sets," in Proceedings of ISSRE, pp. 146-151, 2017.

[2] Weilin Luo, Ou Wei and Hai Wan, "SATMCS: An Efficient SAT-Based Algorithm and Its Improvements for Computing Minimal Cut Sets," IEEE Transactions on Reliability, 2020.

---
## Environment
- Ubuntu 18.04
- python 2.7

---
## Quick start
```
sh run.sh
```

---
## Parameters

|Name|Function|Default value|
|-|-|-|
|bm|set the benchmark|"test"|
|tl|set the time limit (s)|3600|
|omcs|set whether to output MCSs (0: False; 1: True)|0|
|bt|set the backtrack mode (0: backtrack; 1: backjump)|1|

## Directory Overview:

|Name|Function|
|-|-|
|`./example`|Benchmarks|
|`./example/output`|results (.res)|

## Framework

`f.dag` -> |Simplify| -> |Module| -> |Compute| -> |Merge| -> `f.res`

|Name|Function|Input|Output|
|-|-|-|-|
|Simplify|simplify the fault tree|`f.dag`|`f.sdag`|
|Module|module division for the fault tree|`f.sdag`|`f_mi.sdag`, `f_mi-p.cnf`, `f_mi-n.cnf`, and map of `f_mi.sdag`|
|Compute|compute all MCSs of the fault tree|`f_mi.sdag`, `f_mi-p.cnf`, `f_mi-n.cnf`, and map of `f_mi.sdag`|`f_mi.mcs`|
|Merge|merge the MCSs of modules|`f_mi.mcs`, and map of `f_mi.sdag`|`f_mi.mcs`|

## Algorithm

### Simplify and Module (Preprocessing)

We use a well-known preprocessing method [3].

[3] Yves Dutuit, Antoine Rauzy, "A linear-time algorithm to find modules of fault trees," IEEE Transactions on Reliability, vol. 45, no. 3, pp. 422-425, 1996.

https://github.com/chent86/fault_tree_preprocess

### SATMCS

Luo and Wei proposed a SAT-based method, namely SATMCS, which reformulates the problem of representing MCSs as the problem of searching models. 
SATMCS extracts an MCS utilizing local propagation graph (LPG).
The LPG based on graph explicitly represents how the status of system components lead to a system failure through the structure of the fault tree. 
Experiments show that SATMCS efficiently computes MCSs with lower memory cost. 

https://ieeexplore.ieee.org/document/8109081/

