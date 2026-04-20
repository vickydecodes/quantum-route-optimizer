/**
 * MetricsCard
 * Displays real-world metrics computed from OSRM road distance.
 */
export default function MetricsCard({ result }) {
  if (!result) return null;

  const metrics = [
    { label: "Road Distance",   icon: "📍", value: `${result.distance_km} km` },
    { label: "Est. Drive Time", icon: "⏱",  value: `${result.time_minutes} min` },
    { label: "Fuel Cost",       icon: "⛽",  value: `₹${result.fuel_cost_inr}` },
    { label: "CO₂ Emitted",     icon: "🌿",  value: `${result.co2_grams} g` },
  ];

  return (
    <div className="card">
      <h2>📊 Route Metrics</h2>
      <p className="description">
        Computed from real OSRM road distance ·
        35 km/h avg · ₹102/L petrol · 12 km/L · 2310 g CO₂/L
      </p>

      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <div className="metric-tile" key={i}>
            <div className="metric-tile-label">{m.icon} {m.label}</div>
            <div className="metric-value" style={{ fontSize: 22, marginTop: 6 }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 20, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="algo-badge">
          <strong style={{ color: "#60a5fa" }}>Quantum:</strong><br />
          {result.quantum_algo}
        </div>
        <div className="algo-badge">
          <strong style={{ color: "#34d399" }}>Classical:</strong><br />
          {result.classical_algo}
        </div>
      </div>

      <div className="algo-badge" style={{ marginTop: 12 }}>
        <strong style={{ color: "#fbbf24" }}>Winner → {result.algorithm}</strong>
        {result.improvement_pct > 0 && (
          <span style={{ color: "#4ade80", marginLeft: 8 }}>
            ({result.improvement_pct}% shorter than the other)
          </span>
        )}
      </div>
    </div>
  );
}