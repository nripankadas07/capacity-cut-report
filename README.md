# capacity-cut-report

Compute integer max flow for explicit pool/task links, report idle and unfilled units, and expose cut edges whose capacity certifies the achieved maximum.

For: Operations engineers checking aggregate pool-to-task capacity compatibility in a single planning period. Total capacity can equal total demand while eligibility restrictions still leave demand unmet; an allocation alone does not explain the unavoidable bottleneck.

## Quickstart

Python 3.10 or newer. No runtime packages or network requests. The initial wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/capacity-cut-report.git
cd capacity-cut-report
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/capacity-cut-report example.json
```

The synthetic example intentionally exits1: fulfilled6, shortfall2 and idle2 despite total capacity8. Cut capacity6 equals maximum flow; this exposes the compatibility bottleneck.

Windows: use `.venv\Scripts\python.exe` and `.venv\Scripts\capacity-cut-report.exe` instead. Windows is documented but has not been executed in this release's Linux CI.

## Input and result contract

Strict UTF-8 JSON <=2 MiB with exact keys pools,tasks,links. Pools/tasks <=64 each, unique IDs1..128 printable characters; capacity/demand are integers0..1000000000 (booleans/floats rejected). Links <=4096 unique pool/task pairs, known endpoints, optional integer limit in the same range; absent limit equals total demand. IDs may repeat across pool/task namespaces. Deterministic sorted traversal; breadth-first residual augmentation permits rerouting. Certificate includes residual reachable sets, cut edges and cut_capacity==fulfilled. Duplicate/unknown JSON keys and nonfinite values fail.

Output is JSON on stdout. Exit 0 means complete/no findings; exit 1 means a valid report with missing coverage, prices, capacity, or capture findings, where applicable. SQLite extraction has no exit-1 state. Exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes command options. Inputs stay local; review output before sharing it.

## Limits

Fungible integer units in one static period only. No dates, shifts, costs, preferences, indivisible jobs, individual employee assignment, fairness or optimization beyond maximum feasible units. Minimum cuts/allocations can be nonunique; input-order stability does not make an allocation uniquely correct. Compatibility and capacity are caller supplied. The certificate proves only the stated mathematical model.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/capacity-cut-report-check
/tmp/capacity-cut-report-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/capacity-cut-report-check/bin/python
```

The installed-command check runs outside the checkout. See [validation](VALIDATION.md), [research and tradeoffs](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and synthetic fixtures, developed with AI assistance and reviewed through executable checks. MIT license. No customer/adoption claims, copied competitor implementation, or performance-superiority claim.
