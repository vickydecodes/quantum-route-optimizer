import { useState } from "react";

const PRESETS = [
  { label: "Chennai → Bangalore",
    locations: [{ lat: "13.0827", lng: "80.2707" }, { lat: "12.9716", lng: "77.5946" }] },
  { label: "Mumbai → Pune",
    locations: [{ lat: "19.0760", lng: "72.8777" }, { lat: "18.5204", lng: "73.8567" }] },
  { label: "Delhi → Agra",
    locations: [{ lat: "28.6139", lng: "77.2090" }, { lat: "27.1767", lng: "78.0081" }] },
  { label: "Hyderabad → Vijayawada",
    locations: [{ lat: "17.3850", lng: "78.4867" }, { lat: "16.5062", lng: "80.6480" }] },
];

export default function LocationForm({ onSubmit, loading }) {
  const [locations, setLocations] = useState([
    { lat: "", lng: "" },
    { lat: "", lng: "" },
  ]);

  const update = (idx, field, val) => {
    const copy = [...locations];
    copy[idx][field] = val;
    setLocations(copy);
  };

  const addRow    = () => setLocations([...locations, { lat: "", lng: "" }]);
  const removeRow = (idx) => {
    if (locations.length <= 2) return;
    setLocations(locations.filter((_, i) => i !== idx));
  };
  const applyPreset = (p) => setLocations(p.locations.map((l) => ({ ...l })));

  const handleSubmit = () => {
    const valid = locations.filter((l) => l.lat.trim() && l.lng.trim());
    onSubmit(valid);
  };

  return (
    <div className="card">
      <h2>📍 Delivery Locations</h2>
      <p className="description">Enter coordinates or pick a preset to get started quickly.</p>

      {/* Presets */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20 }}>
        {PRESETS.map((p) => (
          <button key={p.label} className="btn-secondary"
            style={{ fontSize: 11, padding: "6px 14px" }}
            onClick={() => applyPreset(p)}>
            {p.label}
          </button>
        ))}
      </div>

      {/* Column headers */}
      <div style={{ display: "grid", gridTemplateColumns: "28px 1fr 1fr 36px",
                    gap: 10, marginBottom: 6 }}>
        <span /><span className="input-label">Latitude</span>
        <span className="input-label">Longitude</span><span />
      </div>

      {/* Rows */}
      {locations.map((loc, idx) => (
        <div key={idx} style={{ display: "grid",
          gridTemplateColumns: "28px 1fr 1fr 36px",
          gap: 10, marginBottom: 10, alignItems: "center" }}>
          <div className="loc-index">{idx + 1}</div>
          <input className="input" type="number" step="any"
            placeholder="e.g. 13.0827" value={loc.lat}
            onChange={(e) => update(idx, "lat", e.target.value)} />
          <input className="input" type="number" step="any"
            placeholder="e.g. 80.2707" value={loc.lng}
            onChange={(e) => update(idx, "lng", e.target.value)} />
          <button className="btn-remove" onClick={() => removeRow(idx)}
            disabled={locations.length <= 2}>✕</button>
        </div>
      ))}

      <div className="btn-row">
        <button className="btn-secondary" onClick={addRow}>＋ Add Stop</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? "⏳ Optimising…" : "⚡ Optimize Route"}
        </button>
      </div>
    </div>
  );
}