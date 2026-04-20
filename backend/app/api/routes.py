"""
routes.py
─────────
Pipeline for /api/optimize:

  1. Quantum (QAOA via Qiskit/Aer)  → determines optimal visit ORDER
  2. Classical (Greedy+2opt+SA)     → independently finds shortest order
  3. Pick winner                    → whichever has shorter STRAIGHT-LINE distance
  4. OSRM                           → fetch real ROAD geometry for the winning route
  5. Return road polyline + metrics to the frontend

The frontend draws ONE route line that follows actual roads.
"""

import httpx
from fastapi import APIRouter, HTTPException
from app.models.schema import DeliveryRequest
from app.algorithms.classical import classical_optimization
from app.algorithms.quantum import quantum_optimization
from app.core.distance import haversine_distance, distance_to_metrics
from app.models.db import routes_collection

router = APIRouter(prefix="/api")

OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"


# ── Straight-line distance for a route order ──────────────────────────────────

def _sl_distance(route: list, locations) -> float:
    dist = 0.0
    for i in range(len(route) - 1):
        a = locations[route[i]]
        b = locations[route[i + 1]]
        dist += haversine_distance(a.lat, a.lng, b.lat, b.lng)
    return dist


# ── Fetch road geometry from OSRM ─────────────────────────────────────────────

def _osrm_road_route(ordered_locs: list) -> dict:
    """
    Calls OSRM /route/v1/driving with the ordered stop list.
    Returns { geometry: [[lng,lat],...], distance_km, duration_sec }.
    Falls back to straight-line if OSRM is unreachable.
    """
    coords = ";".join(f"{loc.lng},{loc.lat}" for loc in ordered_locs)
    url    = f"{OSRM_BASE}/{coords}"
    params = {"overview": "full", "geometries": "geojson", "steps": "false"}

    try:
        resp = httpx.get(url, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError(f"OSRM: {data.get('code')}")

        r        = data["routes"][0]
        geometry = r["geometry"]["coordinates"]   # [[lng, lat], ...]
        dist_km  = round(r["distance"] / 1000, 3)
        dur_sec  = round(r["duration"], 1)

        return {"geometry": geometry, "distance_km": dist_km, "duration_sec": dur_sec}

    except Exception as e:
        print(f"⚠️  OSRM fallback (straight lines): {e}")
        # Fallback: straight lines between stops
        geometry = [[loc.lng, loc.lat] for loc in ordered_locs]
        dist_km  = round(_sl_distance(list(range(len(ordered_locs))), ordered_locs), 3)
        return {"geometry": geometry, "distance_km": dist_km, "duration_sec": 0}


# ── POST /api/optimize ────────────────────────────────────────────────────────

@router.post("/optimize")
def optimize(data: DeliveryRequest):
    if len(data.locations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 locations required.")

    locs = data.locations

    # Step 1: Both algorithms produce an ordered route (list of indices)
    q_result = quantum_optimization(locs)
    c_result = classical_optimization(locs)

    q_route = q_result["route"]
    c_route = c_result["route"]

    # Step 2: Pick the route with shorter straight-line distance
    q_dist = _sl_distance(q_route, locs) if q_route else float("inf")
    c_dist = _sl_distance(c_route, locs) if c_route else float("inf")

    if q_dist <= c_dist:
        best_route     = q_route
        winning_algo   = q_result["algorithm"]
        sl_dist        = q_dist
    else:
        best_route     = c_route
        winning_algo   = c_result["algorithm"]
        sl_dist        = c_dist

    improvement_pct = round(abs(q_dist - c_dist) / max(q_dist, c_dist) * 100, 2) \
                      if max(q_dist, c_dist) > 0 else 0.0
    winner = "quantum" if q_dist <= c_dist else "classical"

    # Step 3: Ordered location objects for the winning route
    ordered_locs = [locs[i] for i in best_route]

    # Step 4: Fetch real road geometry from OSRM
    road = _osrm_road_route(ordered_locs)

    # Step 5: Compute real-world metrics from road distance
    metrics = distance_to_metrics(road["distance_km"])

    response = {
        "status":          "success",
        "route_order":     best_route,           # stop index order
        "geometry":        road["geometry"],     # [[lng,lat],...] road coords
        "distance_km":     road["distance_km"],  # real road km
        "duration_sec":    road["duration_sec"], # OSRM drive time
        "time_minutes":    metrics["time_minutes"],
        "fuel_cost_inr":   metrics["fuel_cost_inr"],
        "co2_grams":       metrics["co2_grams"],
        "algorithm":       winning_algo,
        "winner":          winner,
        "improvement_pct": improvement_pct,
        "quantum_algo":    q_result["algorithm"],
        "classical_algo":  c_result["algorithm"],
    }

    # Persist (best-effort)
    if routes_collection is not None:
        try:
            routes_collection.insert_one({
                "locations": [loc.dict() for loc in locs],
                **{k: v for k, v in response.items() if k != "geometry"},
            })
        except Exception as e:
            print(f"⚠️  DB insert failed: {e}")

    return response


# ── GET /api/history ──────────────────────────────────────────────────────────

@router.get("/history")
def get_history(limit: int = 10):
    if routes_collection is None:
        return {"history": []}
    history = list(routes_collection.find().sort("_id", -1).limit(limit))
    for item in history:
        item["_id"] = str(item["_id"])
    return {"history": history}


@router.get("/health")
def health():
    return {"status": "ok", "db": routes_collection is not None}