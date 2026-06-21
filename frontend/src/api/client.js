/**
 * Thin wrapper around the Phase 1 + 2 FastAPI backend.
 * Centralizing this in one file means: change the base URL once, handle
 * errors once, and every component below just calls plain async functions
 * instead of repeating fetch boilerplate everywhere.
 */
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "dev-secret";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,        // required by backend auth
    },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON; fall back to statusText
    }
    throw new Error(`${res.status}: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

// ---------- Patients ----------
export const getPatients = () => request("/patients/");
export const getPatient = (id) => request(`/patients/${id}`);
export const createPatient = (data) =>
  request("/patients/", { method: "POST", body: JSON.stringify(data) });
export const deletePatient = (id) =>
  request(`/patients/${id}`, { method: "DELETE" });

// ---------- Conditions ----------
export const getConditions = () => request("/conditions/");

// ---------- Visits ----------
export const getAllVisits = () => request("/visits/");
export const getPatientVisits = (patientId) => request(`/visits/patient/${patientId}`);
export const createVisit = (data) =>
  request("/visits/", { method: "POST", body: JSON.stringify(data) });
export const getModelInfo = () => request("/visits/model-info");

// ---------- Disease Prediction (separate, non-clinical demo feature) ----------
export const getAvailableSymptoms = () => request("/symptoms/available");
export const getDiseaseModelInfo = () => request("/symptoms/model-info");
export const predictDisease = (symptoms) =>
  request("/symptoms/predict", { method: "POST", body: JSON.stringify({ symptoms }) });
