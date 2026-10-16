import copy
import itertools
import random
import unittest
from capacity_cut_report import analyze


def case():
    return {'pools': [{'id': 'A', 'capacity': 3}, {'id': 'B', 'capacity': 5}],
            'tasks': [{'id': 'X', 'demand': 5}, {'id': 'Y', 'demand': 3}],
            'links': [{'pool': 'A', 'task': 'X'}, {'pool': 'B', 'task': 'Y'}]}


class CapacityTests(unittest.TestCase):
    def test_eligibility_bottleneck_with_idle_capacity(self):
        r = analyze(case())
        self.assertEqual((r['fulfilled'], r['shortfall']), (6, 2))
        self.assertEqual(r['pools'][1]['idle'], 2)
        self.assertEqual(r['certificate']['cut_capacity'], 6)
        self.assertEqual({e['kind'] for e in r['certificate']['cut_edges']}, {'pool_capacity', 'task_demand'})

    def test_reverse_residual_reroutes_initial_assignment(self):
        d = {'pools': [{'id': 'A', 'capacity': 1}, {'id': 'B', 'capacity': 1}],
             'tasks': [{'id': 'X', 'demand': 1}, {'id': 'Y', 'demand': 1}],
             'links': [{'pool': 'A', 'task': 'X'}, {'pool': 'A', 'task': 'Y'}, {'pool': 'B', 'task': 'X'}]}
        self.assertEqual(analyze(d)['allocations'], [{'pool': 'A', 'task': 'Y', 'units': 1}, {'pool': 'B', 'task': 'X', 'units': 1}])

    def test_permutation_stability(self):
        d = case()
        r = analyze(d)
        for k in d:
            d[k].reverse()
        self.assertEqual(r, analyze(d))

    def test_link_limit_is_a_cut_edge(self):
        d = {'pools': [{'id': 'A', 'capacity': 9}], 'tasks': [{'id': 'X', 'demand': 8}], 'links': [{'pool': 'A', 'task': 'X', 'limit': 2}]}
        r = analyze(d)
        self.assertEqual(r['fulfilled'], 2)
        self.assertEqual(r['certificate']['cut_edges'], [{'kind': 'compatibility_limit', 'pool': 'A', 'task': 'X', 'capacity': 2}])

    def test_zero_and_empty(self):
        self.assertEqual(analyze({'pools': [], 'tasks': [], 'links': []})['fulfilled'], 0)
        d = case();d['links'] = []
        self.assertEqual(analyze(d)['shortfall'], 8)

    def test_same_pool_and_task_label_do_not_collide(self):
        d = {'pools': [{'id': 'source', 'capacity': 2}], 'tasks': [{'id': 'source', 'demand': 2}], 'links': [{'pool': 'source', 'task': 'source'}]}
        self.assertEqual(analyze(d)['fulfilled'], 2)

    def test_unknown_keys(self):
        for loc in ['root', 'pools', 'tasks', 'links']:
            d = case()
            (d if loc == 'root' else d[loc][0])['extra'] = 1
            with self.subTest(loc=loc), self.assertRaises(ValueError):
                analyze(d)

    def test_invalid_integral_units(self):
        for value in [True, -1, 1.5, '3', 10**9 + 1]:
            d = case();d['pools'][0]['capacity'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyze(d)

    def test_duplicate_ids_and_links(self):
        for key in ['pools', 'tasks', 'links']:
            d = case();d[key].append(copy.deepcopy(d[key][0]))
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(d)

    def test_unknown_link_endpoint(self):
        d = case();d['links'][0]['task'] = 'absent'
        with self.assertRaises(ValueError):
            analyze(d)

    def test_nonprinting_identifiers_refused(self):
        for value in ['A\x7f', 'A\u200b', 'A\u202e', 'A\x00']:
            d=case();d['pools'][0]['id']=value
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyze(d)

    def test_node_limit(self):
        d = {'pools': [{'id': str(i), 'capacity': 1} for i in range(65)], 'tasks': [], 'links': []}
        with self.assertRaises(ValueError):
            analyze(d)

    def test_large_integer_capacity_is_exact(self):
        d = {'pools': [{'id': 'A', 'capacity': 10**9}], 'tasks': [{'id': 'X', 'demand': 10**9}], 'links': [{'pool': 'A', 'task': 'X'}]}
        self.assertEqual(analyze(d)['fulfilled'], 10**9)

    def test_random_small_networks_against_exhaustive_cuts(self):
        rng = random.Random(107)
        for _ in range(100):
            pc = [rng.randrange(5) for _ in range(2)]
            td = [rng.randrange(5) for _ in range(2)]
            caps = [[rng.randrange(5) for _ in range(2)] for _ in range(2)]
            d = {'pools': [{'id': str(i), 'capacity': pc[i]} for i in range(2)],
                 'tasks': [{'id': str(i), 'demand': td[i]} for i in range(2)],
                 'links': [{'pool': str(i), 'task': str(j), 'limit': caps[i][j]} for i in range(2) for j in range(2)]}
            values = []
            for mask in itertools.product((False, True), repeat=4):
                values.append(sum(pc[i] for i in range(2) if not mask[i]) +
                              sum(caps[i][j] for i in range(2) for j in range(2) if mask[i] and not mask[2+j]) +
                              sum(td[j] for j in range(2) if mask[2+j]))
            r = analyze(d)
            self.assertEqual(r['fulfilled'], min(values))
            for p in r['pools']:
                self.assertLessEqual(p['used'], p['capacity'])
            for t in r['tasks']:
                self.assertLessEqual(t['fulfilled'], t['demand'])


if __name__ == '__main__':
    unittest.main()
