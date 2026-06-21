/**
 * Persistent, non-dismissible disclaimer for the disease prediction
 * feature. Deliberately impossible to permanently hide (no "don't show
 * again" option) -- rendered every single time a prediction is shown,
 * not just on first use. This is a hard project requirement, not a
 * cosmetic choice: see README "Disease Prediction" section.
 */
export default function DiseaseDisclaimer() {
  return (
    <div className="bg-amber-50 border border-amber-300 rounded-lg px-4 py-3 text-sm text-amber-900 flex gap-2.5">
      <span className="text-amber-500 flex-shrink-0">⚠</span>
      <p>
        <strong>Not a medical diagnosis.</strong> This is a non-clinical demo
        trained on a synthetic/templated public dataset, not real patient
        records. Symptom overlap with a disease name below does not mean you
        have that condition. Always consult a qualified healthcare
        professional for any real health concern.
      </p>
    </div>
  );
}
