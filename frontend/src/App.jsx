import { useState } from "react";
import LocationForm from "./components/LocationForm";
import MapView from "./components/MapView";
import MetricsCard from "./components/MetricsCard";
import ComparisonChart from "./components/ComparisonChart";
import { optimizeRoutes } from "./api/optimize";
import "./App.css";

export default function App() {
  const [locations,  setLocations]  = useState([]);
  const [result,     setResult]     = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState(null);

  const handleOptimize = async (locs) => {
    const clean = locs
      .map((l) => ({ lat: parseFloat(l.lat), lng: parseFloat(l.lng) }))
      .filter((l) => !isNaN(l.lat) && !isNaN(l.lng));

    if (clean.length < 2) {
      setError("Please enter at least 2 valid locations.");
      return;
    }

    setError(null);
    setLoading(true);
    setResult(null);

    try {
      setLocations(clean);
      const res = await optimizeRoutes(clean);
      setResult(res);
    } catch (e) {
      setError("Optimization failed — is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-badge">⚛ QUANTUM × CLASSICAL</div>
        <h1 className="title">Route Optimizer</h1>
        <p className="subtitle">
          Quantum QAOA selects optimal stop order · Classical SA refines it · OSRM draws real roads
        </p>
      </header>

      <section className="section">
        <LocationForm onSubmit={handleOptimize} loading={loading} />
        {error && <div className="error-banner">⚠ {error}</div>}
      </section>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
          <p>Running QAOA + Classical + fetching road geometry…</p>
        </div>
      )}

      {/* Map always shows once we have locations */}
      {locations.length >= 2 && (
        <section className="section">
          <MapView
            locations={locations}
            result={result}
          />
        </section>
      )}

      {result && (
        <>
          <div className={`winner-banner winner-${result.winner}`}>
            🏆 {result.winner === "quantum" ? "Quantum" : "Classical"} route won
            {result.improvement_pct > 0 && ` · ${result.improvement_pct}% shorter`}
            &nbsp;· Road distance: <strong>{result.distance_km} km</strong>
          </div>

          <section className="section">
            <MetricsCard result={result} />
          </section>

          <section className="section">
            <ComparisonChart result={result} />
          </section>
        </>
      )}
    </div>
  );
}