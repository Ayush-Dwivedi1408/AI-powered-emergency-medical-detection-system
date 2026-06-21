/**
 * Small visual flag so it's always clear in the UI whether a risk score
 * came from the trained model or the rule-based fallback. This mirrors
 * the backend's risk_engine field -- transparency carried all the way
 * through to the UI, not just the API response.
 */
export default function RiskEngineTag({ engine }) {
  if (!engine) return null;
  const isML = engine === "ml_model";
  return (
    <span
      className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded ${
        isML ? "bg-indigo-100 text-indigo-700" : "bg-gray-200 text-gray-600"
      }`}
      title={isML ? "Scored by trained ML model" : "Scored by rule-based fallback (vitals incomplete or model unavailable)"}
    >
      {isML ? "ML" : "Rule-based"}
    </span>
  );
}
