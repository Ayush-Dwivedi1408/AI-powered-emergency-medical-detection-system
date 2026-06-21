import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import PatientDetail from "./pages/PatientDetail";
import NewPatient from "./pages/NewPatient";
import Analytics from "./pages/Analytics";
import SymptomChecker from "./pages/SymptomChecker";

function NavBar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
      <span className="font-bold text-gray-800">🚑 Emergency DSS</span>
      <Link
        to="/"
        className={`text-sm font-medium ${isActive("/") ? "text-indigo-600" : "text-gray-500 hover:text-gray-800"}`}
      >
        Dashboard
      </Link>
      <Link
        to="/analytics"
        className={`text-sm font-medium ${isActive("/analytics") ? "text-indigo-600" : "text-gray-500 hover:text-gray-800"}`}
      >
        Analytics
      </Link>
      <Link
        to="/symptom-checker"
        className={`text-sm font-medium ${isActive("/symptom-checker") ? "text-indigo-600" : "text-gray-500 hover:text-gray-800"}`}
      >
        Symptom Checker
      </Link>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients/new" element={<NewPatient />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/symptom-checker" element={<SymptomChecker />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
