"""Allocate fungible integer capacity and expose a max-flow/min-cut certificate."""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024


def obj(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ValueError("object keys must be: " + ", ".join(required) + ("; optional " + ", ".join(optional) if optional else ""))


def ident(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or not value.isprintable():
        raise ValueError("IDs must contain 1..128 printable characters")
    return value


def integer(value):
    if type(value) is not int or not 0 <= value <= 10**9:
        raise ValueError("capacities and demands must be integers in 0..1000000000")
    return value


def analyze(data):
    obj(data, ("pools", "tasks", "links"))
    for key, cap in (("pools", 64), ("tasks", 64), ("links", 4096)):
        if not isinstance(data[key], list) or len(data[key]) > cap:
            raise ValueError(f"{key} must be an array with at most {cap} entries")
    pools, tasks = {}, {}
    for key, out, qty in (("pools", pools, "capacity"), ("tasks", tasks, "demand")):
        for item in data[key]:
            obj(item, ("id", qty))
            name = ident(item["id"])
            if name in out:
                raise ValueError("duplicate " + key + " ID")
            out[name] = integer(item[qty])
    total_demand = sum(tasks.values())
    links = {}
    for item in data["links"]:
        obj(item, ("pool", "task"), ("limit",))
        pair = ident(item["pool"]), ident(item["task"])
        if pair[0] not in pools or pair[1] not in tasks or pair in links:
            raise ValueError("link has an unknown ID or duplicates a pool/task pair")
        links[pair] = integer(item["limit"]) if "limit" in item else total_demand
    pn, tn = sorted(pools), sorted(tasks)
    source, sink = 0, len(pn) + len(tn) + 1
    pi = {p: 1 + i for i, p in enumerate(pn)}
    ti = {t: 1 + len(pn) + i for i, t in enumerate(tn)}
    graph = [[] for _ in range(sink + 1)]
    original = []

    def edge(u, v, cap, description):
        forward = [v, len(graph[v]), cap]
        backward = [u, len(graph[u]), 0]
        graph[u].append(forward)
        graph[v].append(backward)
        original.append((u, v, cap, forward, description))

    for p in pn:
        edge(source, pi[p], pools[p], {"kind": "pool_capacity", "pool": p})
    for (p, t), cap in sorted(links.items()):
        edge(pi[p], ti[t], cap, {"kind": "compatibility_limit", "pool": p, "task": t})
    for t in tn:
        edge(ti[t], sink, tasks[t], {"kind": "task_demand", "task": t})
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for i, (v, _, residual) in enumerate(graph[u]):
                if residual and v not in parent:
                    parent[v] = (u, i)
                    queue.append(v)
        if sink not in parent:
            reachable = set(parent)
            break
        value = total_demand + 1
        v = sink
        while v != source:
            u, i = parent[v]
            value = min(value, graph[u][i][2])
            v = u
        v = sink
        while v != source:
            u, i = parent[v]
            item = graph[u][i]
            item[2] -= value
            graph[v][item[1]][2] += value
            v = u
        flow += value
    allocation, cut = [], []
    used = {p: 0 for p in pn}
    filled = {t: 0 for t in tn}
    for u, v, cap, item, desc in original:
        sent = cap - item[2]
        if desc["kind"] == "compatibility_limit" and sent:
            allocation.append({"pool": desc["pool"], "task": desc["task"], "units": sent})
            used[desc["pool"]] += sent
            filled[desc["task"]] += sent
        if u in reachable and v not in reachable:
            cut.append({**desc, "capacity": cap})
    cut_capacity = sum(x["capacity"] for x in cut)
    if cut_capacity != flow or sum(filled.values()) != flow or sum(used.values()) != flow:
        raise RuntimeError("internal flow certificate failed")
    return {"total_demand": total_demand, "fulfilled": flow, "shortfall": total_demand - flow,
            "allocations": allocation,
            "pools": [{"id": p, "capacity": pools[p], "used": used[p], "idle": pools[p] - used[p]} for p in pn],
            "tasks": [{"id": t, "demand": tasks[t], "fulfilled": filled[t], "unfilled": tasks[t] - filled[t]} for t in tn],
            "certificate": {"cut_capacity": cut_capacity, "equals_max_flow": True, "cut_edges": cut,
                            "reachable_pools": [p for p in pn if pi[p] in reachable],
                            "reachable_tasks": [t for t in tn if ti[t] in reachable]}}


def load(path):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError("duplicate JSON key")
            d[k] = v
        return d
    with Path(path).open("rb") as f:
        raw = f.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds 2 MiB")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON value")))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="explicit pools/tasks/links JSON")
    a = p.parse_args()
    try:
        report = analyze(load(a.input))
        print(json.dumps(report, sort_keys=True, indent=2))
        return 1 if report["shortfall"] else 0
    except (ValueError, OSError, UnicodeError, RecursionError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
