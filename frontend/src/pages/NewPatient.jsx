import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createPatient } from "../api/client";

export default function NewPatient() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const patient = await createPatient({ name, age: Number(age) });
      navigate(`/patients/${patient.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6 max-w-md mx-auto">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Back to dashboard
      </Link>
      <h1 className="text-2xl font-bold text-gray-800 mt-2 mb-6">Register New Patient</h1>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg mb-4 border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 space-y-3">
        <input
          type="text"
          placeholder="Patient name"
          required
          className="border rounded-lg px-3 py-2 text-sm w-full"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="number"
          placeholder="Age"
          required
          min="1"
          max="130"
          className="border rounded-lg px-3 py-2 text-sm w-full"
          value={age}
          onChange={(e) => setAge(e.target.value)}
        />
        <button
          type="submit"
          disabled={submitting}
          className="bg-indigo-600 text-white rounded-lg py-2 text-sm font-medium w-full hover:bg-indigo-700 disabled:opacity-50"
        >
          {submitting ? "Registering..." : "Register Patient"}
        </button>
      </form>
    </div>
  );
}
