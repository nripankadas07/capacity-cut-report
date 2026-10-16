# Research and scope — 16 October 2026

## Brief

User: Operations engineers checking aggregate pool-to-task capacity compatibility in a single planning period.

Pain: Total capacity can equal total demand while eligibility restrictions still leave demand unmet; an allocation alone does not explain the unavoidable bottleneck.

Smallest useful capability: Compute integer max flow for explicit pool/task links, report idle and unfilled units, and expose cut edges whose capacity certifies the achieved maximum.

Acceptance: Synthetic capacity8/demand8 with restricted compatibility fulfills6, leaves2 idle and2 unmet, and a cut of capacity6. Reverse residual rerouting and100 seeded two-pool/two-task networks match independently enumerated cut minima.

Demand is inferred from the workflow and adjacent public discussions, not a verified request for this project. Discovery: precise GitHub topics, this runnable example and the chronological profile index; no unsolicited outreach or activity manipulation.

## Comparables

Live GitHub repository search, sort **Most stars**, query `networkx in:name`. Highest-star relevant comparable found within this search scope: **networkx/networkx**. Search coverage is limited; this is not an exhaustive worldwide ranking. Broad queries returned unrelated products and were filtered by the actual user workflow.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [networkx/networkx](https://github.com/networkx/networkx) | 17328 | 2026-10-06T17:42:21Z | False | NOASSERTION |
| [google/or-tools](https://github.com/google/or-tools) | 14206 | 2026-10-15T20:41:37Z | False | Apache-2.0 |
| [Pyomo/pyomo](https://github.com/Pyomo/pyomo) | 2544 | 2026-10-13T18:37:56Z | False | NOASSERTION |

Exact observation times, README blob identities and up to five issue/PR references per comparable are in [research provenance](RESEARCH_PROVENANCE.json). NOASSERTION means the API did not classify the license; it is not permission to reuse. Stars are discovery evidence, not a measure of quality, performance or reliability.

NetworkX already provides flow/cut algorithms; OR-Tools includes max flow, assignment and richer optimization; Pyomo models broad optimization problems with solvers. Our original small implementation packages a specific inspectable pool/task workflow without runtime packages. It does not claim algorithmic novelty, faster performance or missing functionality in those systems.

Workflow alternatives: NetworkX for graph modeling, OR-Tools for combinatorial optimization and Pyomo for algebraic models/solver integration. A hand calculation can handle a tiny matrix but does not scale to all compatibility cuts.

Our install is a small Python wheel and two or fewer input steps, with a synthetic example and explicit failure states. Competitors offer broader interfaces, integrations, formats, documentation and support communities; their current READMEs/code and issue discussions were inspected, but their installations, reliability, support response and time to first useful result were not measured here. Our successful example establishes only our stated behavior. Licensing was recorded, not used as a proxy for capability.

Portfolio distinction: task-queue is a queue implementation, grid-ops-arena simulates energy dispatch and value-density-lab scores product outcomes. This is a static aggregate bipartite capacity-allocation/cut certificate tool.

## Claims and reuse

No technical performance benchmark was conducted. There is no speed, memory, reliability or feature-absence superiority claim. Standard algorithms/formats are not inventions of this project. Source references were read for semantics and workflow comparison; implementation, prose and synthetic fixtures were written for this project. No third-party code, font assets or sample user data is bundled. No competitor logos/branding are reused.
