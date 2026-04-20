import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function ComparisonChart({ result }) {
  if (!result) return null;

  const labels = ["Distance (km)", "Time (min)", "Fuel Cost (₹)", "CO₂ (g)"];
  const values = [
    result.distance_km,
    result.time_minutes,
    result.fuel_cost_inr,
    result.co2_grams,
  ];

  const data = {
    labels,
    datasets: [
      {
        label: "Optimised Route",
        data: values,
        backgroundColor: [
          "rgba(0,210,255,0.7)",
          "rgba(0,255,170,0.7)",
          "rgba(251,191,36,0.7)",
          "rgba(52,211,153,0.7)",
        ],
        borderColor: [
          "#00d2ff",
          "#00ffaa",
          "#fbbf24",
          "#34d399",
        ],
        borderWidth: 1,
        borderRadius: 5,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#0d1225",
        borderColor: "rgba(0,210,255,0.2)",
        borderWidth: 1,
        titleColor: "#e8f4ff",
        bodyColor: "#7a9bb5",
        callbacks: {
          label: (ctx) => ` ${ctx.parsed.y.toFixed(2)}`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#7a9bb5", font: { family: "'JetBrains Mono',monospace", size: 11 } },
        grid:  { color: "rgba(255,255,255,0.04)" },
      },
      y: {
        ticks: { color: "#7a9bb5", font: { family: "'JetBrains Mono',monospace", size: 11 } },
        grid:  { color: "rgba(255,255,255,0.06)" },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="chart-container">
      <h2>📈 Route Metrics Overview</h2>
      <Bar data={data} options={options} />
      <p style={{ marginTop: 14, fontSize: 10, color: "#3d5a72", letterSpacing: "0.04em" }}>
        Road distance from OSRM · Time at 35 km/h · Fuel at ₹102/L (12 km/L) · CO₂ at 2310 g/L
      </p>
    </div>
  );
}