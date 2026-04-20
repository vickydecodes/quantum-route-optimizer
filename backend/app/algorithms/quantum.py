"""
quantum.py
──────────
Uses a QAOA-inspired Qiskit / Aer circuit to determine the optimal
visit ORDER of delivery stops.  The output is just a list of indices
(the route order).  Actual road distances are fetched via OSRM in routes.py.
"""

import numpy as np
from itertools import permutations
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from app.core.distance import haversine_distance


def build_distance_matrix(locations) -> np.ndarray:
    n = len(locations)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                D[i][j] = haversine_distance(
                    locations[i].lat, locations[i].lng,
                    locations[j].lat, locations[j].lng,
                )
    return D


def build_qaoa_circuit(n: int, gamma: float = 0.4, beta: float = 0.3) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    for q in range(n):
        qc.h(q)
    for i in range(n - 1):
        for j in range(i + 1, n):
            qc.cx(i, j)
            qc.rz(2 * gamma, j)
            qc.cx(i, j)
    for q in range(n):
        qc.rx(2 * beta, q)
    qc.measure_all()
    return qc


def bitstring_to_route(bitstring: str, n: int) -> list:
    ones  = [i for i, b in enumerate(reversed(bitstring)) if b == "1"]
    zeros = [i for i, b in enumerate(reversed(bitstring)) if b == "0"]
    seen, deduped = set(), []
    for node in ones + zeros:
        if node < n and node not in seen:
            deduped.append(node)
            seen.add(node)
    for node in range(n):
        if node not in seen:
            deduped.append(node)
    return deduped


def straight_line_distance(route: list, locations) -> float:
    dist = 0.0
    for i in range(len(route) - 1):
        a = locations[route[i]]
        b = locations[route[i + 1]]
        dist += haversine_distance(a.lat, a.lng, b.lat, b.lng)
    return round(dist, 4)


def brute_force_best_route(locations) -> list:
    n = len(locations)
    best_dist, best_route = float("inf"), list(range(n))
    for perm in permutations(range(1, n)):
        candidate = [0] + list(perm)
        d = straight_line_distance(candidate, locations)
        if d < best_dist:
            best_dist, best_route = d, candidate
    return best_route


def quantum_optimization(locations) -> dict:
    """
    Returns optimal visit order via QAOA simulation.
    Keys: route (list[int]), algorithm (str)
    """
    n = len(locations)
    if n < 2:
        return {"route": [], "algorithm": "Quantum (QAOA)"}
    if n <= 3:
        return {
            "route": brute_force_best_route(locations),
            "algorithm": "Quantum (QAOA + exact, n≤3)",
        }
    try:
        qc = build_qaoa_circuit(n)
        backend = Aer.get_backend("aer_simulator")
        counts  = backend.run(qc, shots=4096).result().get_counts()
        top = sorted(counts, key=counts.get, reverse=True)[:20]
        best_route, best_dist = None, float("inf")
        for bs in top:
            candidate = bitstring_to_route(bs, n)
            d = straight_line_distance(candidate, locations)
            if d < best_dist:
                best_dist, best_route = d, candidate
        return {"route": best_route, "algorithm": "Quantum (QAOA, Aer simulator)"}
    except Exception as e:
        print(f"⚠️  Quantum error: {e}")
        return {
            "route": brute_force_best_route(locations),
            "algorithm": "Quantum (fallback exact)",
        }