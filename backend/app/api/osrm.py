"""
osrm.py
───────
Fetches real road-following routes from the public OSRM demo server.
Uses the /route/v1/driving endpoint with geometries=geojson.

The returned geometry is a list of [lng, lat] coordinates that perfectly
follow road curves — used by the frontend to draw road-accurate polylines.
"""

import httpx
from typing import List

OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"


async def fetch_road_route(ordered_locations: list) -> dict:
    """
    Given an ORDERED list of Location objects, fetch the road route from
    OSRM covering all stops in sequence.

    Returns:
        {
          "geometry":     [[lng, lat], ...],   # road-following coordinates
          "distance_km":  float,               # real road distance
          "duration_sec": float,               # OSRM estimated drive time
        }
    Raises httpx.HTTPError on network failure.
    """
    # Build coordinate string: "lng,lat;lng,lat;..."
    coords = ";".join(
        f"{loc.lng},{loc.lat}" for loc in ordered_locations
    )
    url = f"{OSRM_BASE}/{coords}"

    params = {
        "overview":   "full",
        "geometries": "geojson",
        "steps":      "false",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = client.get(url, params=params)
        # httpx sync fallback for environments where async isn't wired yet
        if hasattr(resp, "__await__"):
            resp = await resp
        resp.raise_for_status()
        data = resp.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError(f"OSRM error: {data.get('code')} — {data.get('message', '')}")

    route    = data["routes"][0]
    geometry = route["geometry"]["coordinates"]   # list of [lng, lat]
    distance = route["distance"] / 1000           # metres → km
    duration = route["duration"]                  # seconds

    return {
        "geometry":     geometry,
        "distance_km":  round(distance, 3),
        "duration_sec": round(duration, 1),
    }