import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (WGS-84 mean radius)."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Real-world constants (India, delivery van)
AVG_SPEED_KMH          = 35.0
FUEL_L_PER_KM          = 1 / 12.0      # 12 km/L
PETROL_INR_PER_L       = 102.0
CO2_G_PER_L            = 2310.0


def distance_to_metrics(distance_km: float) -> dict:
    litres          = distance_km * FUEL_L_PER_KM
    return {
        "time_minutes":  round((distance_km / AVG_SPEED_KMH) * 60, 2),
        "fuel_cost_inr": round(litres * PETROL_INR_PER_L, 2),
        "co2_grams":     round(litres * CO2_G_PER_L, 2),
    }