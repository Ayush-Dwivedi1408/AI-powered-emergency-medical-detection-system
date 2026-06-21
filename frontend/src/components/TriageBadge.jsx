/**
 * Color-coded badge for triage levels. Centralized here so the
 * P1=red/P2=orange/P3=yellow/P4=green mapping is defined once.
 */
const STYLES = {
  "P1 - IMMEDIATE": "bg-red-100 text-red-800 border-red-300",
  "P2 - URGENT": "bg-orange-100 text-orange-800 border-orange-300",
  "P3 - LESS URGENT": "bg-yellow-100 text-yellow-800 border-yellow-300",
  "P4 - ROUTINE": "bg-green-100 text-green-800 border-green-300",
};

export default function TriageBadge({ level }) {
  if (!level) {
    return (
      <span className="inline-block px-2 py-1 text-xs font-medium rounded-full border bg-gray-100 text-gray-500 border-gray-300">
        No data
      </span>
    );
  }
  const style = STYLES[level] || "bg-gray-100 text-gray-700 border-gray-300";
  return (
    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full border ${style}`}>
      {level}
    </span>
  );
}
