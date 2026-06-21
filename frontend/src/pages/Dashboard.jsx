import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getPatients, getAllVisits } from "../api/client";
import TriageBadge from "../components/TriageBadge";
import RiskEngineTag from "../components/RiskEngineTag";

// Priority order for sorting -- P1 first (most urgent)
const PRIORITY_ORDER = {
  "P1 - IMMEDIATE": 0,
  "P2 - URGENT": 1,
  "P3 - LESS URGENT": 2,
  "P4 - ROUTINE": 3,
};

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [patientData, visitData] = await Promise.all([
          getPatients(),
          getAllVisits(),
        ]);
        setPatients(patientData);
        setVisits(visitData);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // For each patient, find their most recent visit (visits are already
  // sorted desc by created_at from the API) to show "current status".
  const rows = patients.map((p) => {
    const latestVisit = visits.find((v) => v.patient_id === p.id);
    return { patient: p, latestVisit };
  });

  rows.sort((a, b) => {
    const aPriority = a.latestVisit ? PRIORITY_ORDER[a.latestVisit.triage_level] ?? 99 : 99;
    const bPriority = b.latestVisit ? PRIORITY_ORDER[b.latestVisit.triage_level] ?? 99 : 99;
    return aPriority - bPriority;
  });

  if (loading) return <div className="p-6 text-gray-500">Loading dashboard...</div>;
  if (error)
    return (
      <div className="p-6 text-red-600">
        Failed to load: {error}. Is the backend running at the configured API URL?
      </div>
    );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Doctor Dashboard</h1>
        <Link
          to="/patients/new"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          + New Patient
        </Link>
      </div>

      {rows.length === 0 ? (
        <p className="text-gray-500">No patients registered yet.</p>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Patient</th>
                <th className="px-4 py-3 font-medium">Age</th>
                <th className="px-4 py-3 font-medium">Latest Risk</th>
                <th className="px-4 py-3 font-medium">Triage</th>
                <th className="px-4 py-3 font-medium">Engine</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map(({ patient, latestVisit }) => (
                <tr key={patient.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">{patient.name}</td>
                  <td className="px-4 py-3 text-gray-600">{patient.age}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {latestVisit ? `${latestVisit.risk_score}/100` : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <TriageBadge level={latestVisit?.triage_level} />
                  </td>
                  <td className="px-4 py-3">
                    <RiskEngineTag engine={latestVisit?.risk_engine} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/patients/${patient.id}`}
                      className="text-indigo-600 hover:underline font-medium"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
