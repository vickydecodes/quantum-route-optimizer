/**
 * MapView.jsx
 * ───────────
 * Draws the road-following route returned by OSRM.
 * The `result.geometry` field is an array of [lng, lat] pairs that
 * trace actual roads.  Leaflet's <Polyline> connects them accurately.
 */

import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from "react-leaflet";
import { useEffect } from "react";
import L from "leaflet";

// Fix default marker icon (Vite/Leaflet asset issue)
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon   from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl:       markerIcon,
  shadowUrl:     markerShadow,
});

// Glowing numbered marker
function numberedIcon(n, isStart) {
  const bg     = isStart ? "#00ffaa" : "#00d2ff";
  const border = isStart ? "#00ffaa" : "#00d2ff";
  return L.divIcon({
    className: "",
    html: `<div style="
      width:30px;height:30px;border-radius:50%;
      background:#0d1225;border:2.5px solid ${border};
      display:flex;align-items:center;justify-content:center;
      color:${bg};font-size:12px;font-weight:700;
      font-family:'JetBrains Mono',monospace;
      box-shadow:0 0 12px ${bg}88;
    ">${n}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
}

// Auto-fit map to all stop markers
function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length >= 2) {
      map.fitBounds(L.latLngBounds(positions), { padding: [52, 52] });
    }
  }, [positions, map]);
  return null;
}

export default function MapView({ locations, result }) {
  const defaultCenter = locations.length
    ? [locations[0].lat, locations[0].lng]
    : [20.5937, 78.9629];                       // India centre

  // Stop markers: use route_order if available so they're numbered in visit order
  const routeOrder = result?.route_order ?? locations.map((_, i) => i);
  const stopLatLngs = locations.map((l) => [l.lat, l.lng]);

  /**
   * Road geometry from OSRM comes as [[lng, lat], ...]
   * Leaflet needs [[lat, lng], ...] — flip the pairs here.
   */
  const roadPolyline = result?.geometry
    ? result.geometry.map(([lng, lat]) => [lat, lng])
    : [];

  return (
    <div className="card">
      <h2>🗺 Road Route Visualisation</h2>
      <p className="description">
        Route follows actual roads via OSRM &nbsp;·&nbsp;
        {result
          ? `${result.distance_km} km road distance · ${result.time_minutes} min`
          : "Enter locations and click Optimize to see the route"}
      </p>

      <MapContainer
        center={defaultCenter}
        zoom={7}
        style={{ height: "500px", width: "100%", borderRadius: "10px" }}
        scrollWheelZoom
      >
        {/* Dark CartoDB basemap */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          maxZoom={19}
        />

        <FitBounds positions={stopLatLngs} />

        {/* ── Road-following polyline ── */}
        {roadPolyline.length > 1 && (
          <>
            {/* Glow shadow */}
            <Polyline
              positions={roadPolyline}
              color="#00d2ff"
              weight={10}
              opacity={0.15}
            />
            {/* Main road line */}
            <Polyline
              positions={roadPolyline}
              color="#00d2ff"
              weight={4}
              opacity={0.95}
            />
          </>
        )}

        {/* ── Stop markers (numbered in visit order) ── */}
        {routeOrder.map((locIdx, visitIdx) => {
          const loc = locations[locIdx];
          if (!loc) return null;
          return (
            <Marker
              key={locIdx}
              position={[loc.lat, loc.lng]}
              icon={numberedIcon(visitIdx + 1, visitIdx === 0)}
            >
              <Popup>
                <div style={{ fontFamily: "monospace", fontSize: 12 }}>
                  <strong>Stop {visitIdx + 1}</strong><br />
                  Lat: {loc.lat}<br />
                  Lng: {loc.lng}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {result && (
        <div className="map-legend">
          <span>
            <span className="legend-dot" style={{ background: "#00d2ff" }} />
            Road route ({result.winner === "quantum" ? "Quantum-optimised" : "Classical-optimised"})
          </span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "#3d5a72" }}>
            {routeOrder.length} stops · {result.distance_km} km
          </span>
        </div>
      )}
    </div>
  );
}