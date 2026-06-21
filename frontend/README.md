# Frontend Setup

React + Vite + Tailwind dashboard for the Emergency Decision Support Platform.

## 1. Install dependencies
```bash
npm install
```

## 2. Configure the API URL (optional)
```bash
cp .env.example .env
```
Default points to `http://localhost:8000`. Change it only if your backend
runs elsewhere.

## 3. Run the dev server
```bash
npm run dev
```
Opens at http://localhost:5173. **The backend must already be running**
(see `../backend/README.md`) or you'll see "Failed to load" errors —
that's expected and means the frontend is working, just has nothing to
talk to yet.

## Pages
- `/` — Dashboard: patient list sorted by triage priority (P1 first)
- `/patients/new` — Register a new patient
- `/patients/:id` — Patient detail: risk trend chart, log-visit form, visit history
- `/analytics` — Triage distribution, risk score histogram, ML vs rule-based engine usage

## Notes on the code
- `src/api/client.js` is the **only** file that knows the backend's URL/shape.
  Every page imports plain async functions from it instead of calling
  `fetch` directly — this is what makes the API a single source of truth
  to update if backend routes change.
- `risk_engine` (`ml_model` vs `rule_based`) is surfaced visually via
  `RiskEngineTag` everywhere a risk score is shown, so the UI never hides
  which engine produced a given score (matches the Phase 2 transparency
  principle, carried through to the UI).
- No backend logic is duplicated here — sorting by triage priority,
  histogram bucketing, etc. happen client-side on data the API already
  returns, not by recalculating risk scores in JavaScript.
