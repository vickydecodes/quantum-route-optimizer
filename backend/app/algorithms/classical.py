"""
classical.py
────────────
Classical TSP heuristics: Greedy seed → 2-opt → Simulated Annealing.
Returns the optimal visit ORDER (list of indices).
Road distances are fetched via OSRM in routes.py.
"""

import random
from math import exp
from app.core.distance import haversine_distance


def straight_line_distance(route: list, locations) -> float:
    dist = 0.0
    for i in range(len(route) - 1):
        a = locations[route[i]]
        b = locations[route[i + 1]]
        dist += haversine_distance(a.lat, a.lng, b.lat, b.lng)
    return dist


def greedy_route(locations) -> list:
    n = len(locations)
    route, visited = [0], {0}
    for _ in range(n - 1):
        last = route[-1]
        nearest, best_dist = None, float("inf")
        for i in range(n):
            if i not in visited:
                d = haversine_distance(
                    locations[last].lat, locations[last].lng,
                    locations[i].lat, locations[i].lng,
                )
                if d < best_dist:
                    best_dist, nearest = d, i
        route.append(nearest)
        visited.add(nearest)
    return route


def two_opt(route: list, locations) -> tuple:
    best = list(route)
    best_d = straight_line_distance(best, locations)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                if j - i == 1:
                    continue
                candidate = best[:i] + best[i:j][::-1] + best[j:]
                d = straight_line_distance(candidate, locations)
                if d < best_d:
                    best, best_d = candidate, d
                    improved = True
    return best, best_d


def simulated_annealing(locations, route: list) -> tuple:
    if len(route) < 4:
        return route, straight_line_distance(route, locations)
    temp, cooling, min_temp = 1000.0, 0.995, 0.1
    cur, cur_d = list(route), straight_line_distance(route, locations)
    best, best_d = list(cur), cur_d
    inner = list(range(1, len(route) - 1))
    while temp > min_temp:
        if len(inner) < 2:
            break
        i, j = sorted(random.sample(inner, 2))
        new = cur[:i] + cur[i:j][::-1] + cur[j:]
        new_d = straight_line_distance(new, locations)
        if new_d < cur_d or exp(-(new_d - cur_d) / temp) > random.random():
            cur, cur_d = new, new_d
        if cur_d < best_d:
            best, best_d = list(cur), cur_d
        temp *= cooling
    return best, best_d


def classical_optimization(locations) -> dict:
    """
    Returns optimal visit order via classical heuristics.
    Keys: route (list[int]), algorithm (str)
    """
    if len(locations) < 2:
        return {"route": [], "algorithm": "Classical (Greedy+2opt+SA)"}
    route = greedy_route(locations)
    route, _ = two_opt(route, locations)
    route, _ = simulated_annealing(locations, route)
    return {"route": route, "algorithm": "Classical (Greedy + 2-opt + SA)"}