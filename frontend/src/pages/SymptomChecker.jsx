import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAvailableSymptoms, predictDisease, getDiseaseModelInfo } from "../api/client";
import DiseaseDisclaimer from "../components/DiseaseDisclaimer";

export default function SymptomChecker() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [search, setSearch] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    Promise.all([getAvailableSymptoms(), getDiseaseModelInfo()])
      .then(([symptomsData, infoData]) => {
        setAllSymptoms(symptomsData.symptoms);
        setModelInfo(infoData);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function toggleSymptom(symptom) {
    const next = new Set(selected);
    if (next.has(symptom)) {
      next.delete(symptom);
    } else {
      next.add(symptom);
    }
    setSelected(next);
    setResult(null); // clear stale results when selection changes
  }

  async function handlePredict() {
    if (selected.size === 0) return;
    setPredicting(true);
    setError(null);
    try {
      const res = await predictDisease(Array.from(selected));
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setPredicting(false);
    }
  }

  const filteredSymptoms = allSymptoms.filter((s) =>
    s.toLowerCase().replace(/_/g, " ").includes(search.toLowerCase())
  );

  if (loading) return <div className="p-6 text-gray-500">Loading symptom checker...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Back to dashboard
      </Link>
      <h1 className="text-2xl font-bold text-gray-800 mt-2 mb-4">Symptom Checker (Demo)</h1>

      {/* Disclaimer is ALWAYS rendered at the top of this page, before
          any interaction -- not just after a prediction is shown. */}
      <div className="mb-6">
        <DiseaseDisclaimer />
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg mb-4 border border-red-200">
          {error}
        </div>
      )}

      {modelInfo && (
        <p className="text-xs text-gray-400 mb-4">
          Model: {modelInfo.model_name} · {modelInfo.num_symptoms} symptoms ·{" "}
          {modelInfo.num_diseases} diseases · Source: {modelInfo.data_source}
        </p>
      )}

      {/* Symptom selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">
          Select symptoms ({selected.size} selected)
        </h2>
        <input
          type="text"
          placeholder="Search symptoms..."
          className="border rounded-lg px-3 py-2 text-sm w-full mb-3"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-80 overflow-y-auto pr-1">
          {filteredSymptoms.map((symptom) => (
            <label
              key={symptom}
              className="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selected.has(symptom)}
                onChange={() => toggleSymptom(symptom)}
              />
              {symptom.replace(/_/g, " ")}
            </label>
          ))}
        </div>

        <button
          onClick={handlePredict}
          disabled={selected.size === 0 || predicting}
          className="mt-4 bg-indigo-600 text-white rounded-lg py-2 px-4 text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {predicting ? "Checking..." : "Check possible matches"}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-700 mb-3">Statistical matches</h2>

          {/* Disclaimer repeated here too -- directly next to the result,
              not just once at the top of the page, so it's impossible
              to see a prediction without seeing the caveat in the same view. */}
          <div className="mb-4">
            <DiseaseDisclaimer />
          </div>

          {result.top_predictions.length === 0 ? (
            <p className="text-gray-400 text-sm">
              No matches found for the selected symptoms in this dataset.
            </p>
          ) : (
            <div className="space-y-3">
              {result.top_predictions.map((p, idx) => (
                <div
                  key={p.disease}
                  className="border border-gray-100 rounded-lg px-3 py-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {idx + 1}. {p.disease}
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-400"
                          style={{ width: `${Math.min(p.probability * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-12 text-right">
                        {(p.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* First-aid guidance column -- only shown for the
                      top match, since lower-ranked candidates are too
                      uncertain to act on at all. Tier badge makes clear
                      whether this is general OTC-category guidance or
                      a "see a doctor" safe fallback. */}
                  {idx === 0 && (
                    <div className="flex gap-2 mt-2 pt-2 border-t border-gray-100">
                      <span
                        className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded h-fit flex-shrink-0 ${
                          p.first_aid_tier === "serious"
                            ? "bg-red-100 text-red-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {p.first_aid_tier === "serious" ? "See a doctor" : "General care"}
                      </span>
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {p.first_aid_advice}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
