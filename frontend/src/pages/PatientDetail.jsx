import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getPatient, getConditions, createVisit } from "../api/client";
import TriageBadge from "../components/TriageBadge";
import RiskEngineTag from "../components/RiskEngineTag";

const EMPTY_FORM = {
  condition_id: "",
  pulse: "",
  spo2: "",
  temperature: "",
  respiration_rate: "",
  systolic_bp: "",
  is_alert: true,
  has_chest_pain: false,
  has_breathing_diff: false,
  has_bleeding: false,
  notes: "",
};

export default function PatientDetail() {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [conditions, setConditions] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const [patientData, conditionData] = await Promise.all([
        getPatient(id),
        getConditions(),
      ]);
      setPatient(patientData);
      setConditions(conditionData);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createVisit({
        patient_id: Number(id),
        condition_id: form.condition_id ? Number(form.condition_id) : null,
        pulse: form.pulse ? Number(form.pulse) : null,
        spo2: form.spo2 ? Number(form.spo2) : null,
        temperature: form.temperature ? Number(form.temperature) : null,
        respiration_rate: form.respiration_rate ? Number(form.respiration_rate) : null,
        systolic_bp: form.systolic_bp ? Number(form.systolic_bp) : null,
        is_alert: form.is_alert,
        has_chest_pain: form.has_chest_pain,
        has_breathing_diff: form.has_breathing_diff,
        has_bleeding: form.has_bleeding,
        notes: form.notes || null,
      });
      setForm(EMPTY_FORM);
      await load(); // refresh visit history + chart
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="p-6 text-gray-500">Loading patient...</div>;
  if (!patient) return <div className="p-6 text-red-600">Patient not found.</div>;

  const chartData = patient.visits.map((v, idx) => ({
    visit: `Visit ${idx + 1}`,
    risk: v.risk_score,
    date: new Date(v.created_at).toLocaleDateString(),
  }));

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Back to dashboard
      </Link>

      <div className="flex items-baseline justify-between mt-2 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{patient.name}</h1>
        <span className="text-gray-500">Age {patient.age}</span>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg mb-4 border border-red-200">
          {error}
        </div>
      )}

      {/* Risk trend chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Risk Score Trend</h2>
        {chartData.length === 0 ? (
          <p className="text-gray-400 text-sm">No visits logged yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="visit" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="risk" stroke="#4f46e5" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Log new visit form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Log New Visit</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-3">
          <select
            className="border rounded-lg px-3 py-2 text-sm col-span-2"
            value={form.condition_id}
            onChange={(e) => setForm({ ...form, condition_id: e.target.value })}
          >
            <option value="">-- Select condition (optional) --</option>
            {conditions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.base_severity})
              </option>
            ))}
          </select>

          <input
            type="number"
            placeholder="Pulse (bpm)"
            className="border rounded-lg px-3 py-2 text-sm"
            value={form.pulse}
            onChange={(e) => setForm({ ...form, pulse: e.target.value })}
          />
          <input
            type="number"
            step="0.1"
            placeholder="SpO2 (%)"
            className="border rounded-lg px-3 py-2 text-sm"
            value={form.spo2}
            onChange={(e) => setForm({ ...form, spo2: e.target.value })}
          />
          <input
            type="number"
            step="0.1"
            placeholder="Temperature (°C)"
            className="border rounded-lg px-3 py-2 text-sm col-span-2"
            value={form.temperature}
            onChange={(e) => setForm({ ...form, temperature: e.target.value })}
          />

          <div className="col-span-2 text-xs text-gray-400 -mb-1 mt-1">
            NEWS2 score inputs (Royal College of Physicians clinical score)
          </div>
          <input
            type="number"
            placeholder="Respiration rate (/min)"
            className="border rounded-lg px-3 py-2 text-sm"
            value={form.respiration_rate}
            onChange={(e) => setForm({ ...form, respiration_rate: e.target.value })}
          />
          <input
            type="number"
            placeholder="Systolic BP (mmHg)"
            className="border rounded-lg px-3 py-2 text-sm"
            value={form.systolic_bp}
            onChange={(e) => setForm({ ...form, systolic_bp: e.target.value })}
          />
          <label className="col-span-2 flex items-center gap-1.5 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={form.is_alert}
              onChange={(e) => setForm({ ...form, is_alert: e.target.checked })}
            />
            Patient is alert (uncheck if confused / responds only to voice, pain, or unresponsive)
          </label>

          <div className="col-span-2 flex gap-4 text-sm text-gray-600">
            <label className="flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={form.has_chest_pain}
                onChange={(e) => setForm({ ...form, has_chest_pain: e.target.checked })}
              />
              Chest pain
            </label>
            <label className="flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={form.has_breathing_diff}
                onChange={(e) => setForm({ ...form, has_breathing_diff: e.target.checked })}
              />
              Breathing difficulty
            </label>
            <label className="flex items-center gap-1.5">
              <input
                type="checkbox"
                checked={form.has_bleeding}
                onChange={(e) => setForm({ ...form, has_bleeding: e.target.checked })}
              />
              Bleeding
            </label>
          </div>

          <input
            type="text"
            placeholder="Notes (optional)"
            className="border rounded-lg px-3 py-2 text-sm col-span-2"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />

          <button
            type="submit"
            disabled={submitting}
            className="col-span-2 bg-indigo-600 text-white rounded-lg py-2 text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {submitting ? "Submitting..." : "Log Visit"}
          </button>
        </form>
      </div>

      {/* Visit history table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <h2 className="font-semibold text-gray-700 p-4 pb-0">Visit History</h2>
        {patient.visits.length === 0 ? (
          <p className="text-gray-400 text-sm p-4">No visits yet.</p>
        ) : (
          <table className="w-full text-sm mt-2">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Date</th>
                <th className="px-4 py-2 font-medium">Vitals</th>
                <th className="px-4 py-2 font-medium">Risk</th>
                <th className="px-4 py-2 font-medium">Triage</th>
                <th className="px-4 py-2 font-medium">Engine</th>
                <th className="px-4 py-2 font-medium" title="Royal College of Physicians clinical score, independent of the ML model">
                  NEWS2
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {[...patient.visits].reverse().map((v) => (
                <tr key={v.id}>
                  <td className="px-4 py-2 text-gray-500">
                    {new Date(v.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-gray-600">
                    {v.pulse ?? "—"} bpm / {v.spo2 ?? "—"}% / {v.temperature ?? "—"}°C
                  </td>
                  <td className="px-4 py-2 font-medium">{v.risk_score}</td>
                  <td className="px-4 py-2">
                    <TriageBadge level={v.triage_level} />
                  </td>
                  <td className="px-4 py-2">
                    <RiskEngineTag engine={v.risk_engine} />
                  </td>
                  <td className="px-4 py-2 text-gray-600">
                    {v.news2_score != null ? (
                      <span title={`NEWS2 risk level: ${v.news2_risk_level}`}>
                        {v.news2_score} ({v.news2_risk_level})
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
