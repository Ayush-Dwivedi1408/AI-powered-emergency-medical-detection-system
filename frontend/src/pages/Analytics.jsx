import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { Link } from "react-router-dom";
import { getAllVisits } from "../api/client";

const TRIAGE_COLORS = {
  "P1 - IMMEDIATE": "#dc2626",
  "P2 - URGENT": "#ea580c",
  "P3 - LESS URGENT": "#ca8a04",
  "P4 - ROUTINE": "#16a34a",
};

export default function Analytics() {
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAllVisits()
      .then(setVisits)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading analytics...</div>;
  if (error) return <div className="p-6 text-red-600">Failed to load: {error}</div>;

  // Triage distribution (pie chart)
  const triageCounts = {};
  visits.forEach((v) => {
    if (!v.triage_level) return;
    triageCounts[v.triage_level] = (triageCounts[v.triage_level] || 0) + 1;
  });
  const triageData = Object.entries(triageCounts).map(([name, value]) => ({ name, value }));

  // Risk score histogram (bucketed)
  const buckets = [0, 0, 0, 0, 0]; // 0-19, 20-39, 40-59, 60-79, 80-100
  visits.forEach((v) => {
    const idx = Math.min(Math.floor(v.risk_score / 20), 4);
    buckets[idx]++;
  });
  const histogramData = [
    { range: "0-19", count: buckets[0] },
    { range: "20-39", count: buckets[1] },
    { range: "40-59", count: buckets[2] },
    { range: "60-79", count: buckets[3] },
    { range: "80-100", count: buckets[4] },
  ];

  // Engine usage breakdown
  const engineCounts = { ml_model: 0, rule_based: 0 };
  visits.forEach((v) => {
    if (v.risk_engine) engineCounts[v.risk_engine] = (engineCounts[v.risk_engine] || 0) + 1;
  });

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Back to dashboard
      </Link>
      <h1 className="text-2xl font-bold text-gray-800 mt-2 mb-6">Analytics</h1>

      {visits.length === 0 ? (
        <p className="text-gray-500">No visits logged yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h2 className="font-semibold text-gray-700 mb-3">Triage Distribution</h2>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={triageData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={80}
                  label={({ name, value }) => `${value}`}
                >
                  {triageData.map((entry) => (
                    <Cell key={entry.name} fill={TRIAGE_COLORS[entry.name] || "#888"} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h2 className="font-semibold text-gray-700 mb-3">Risk Score Distribution</h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={histogramData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:col-span-2">
            <h2 className="font-semibold text-gray-700 mb-3">Risk Engine Usage</h2>
            <div className="flex gap-6 text-sm text-gray-600">
              <div>
                <span className="font-semibold text-indigo-600">{engineCounts.ml_model}</span> visits scored by ML model
              </div>
              <div>
                <span className="font-semibold text-gray-500">{engineCounts.rule_based}</span> visits scored by rule-based fallback
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              A high rule-based count usually means vitals (pulse/SpO2/temperature) were left blank when logging visits.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
