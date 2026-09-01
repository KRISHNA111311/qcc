# QCC Phase 0 Verification Checklist

## 1. Database & Setup
- [ ] SQLite database file created (qcc.db)
- [ ] All tables initialized (users, courses, modules, lessons, etc.)
- [ ] No database connection errors on startup
- [ ] .env file properly configured

## 2. API Endpoints
- [ ] GET /api/health - returns {"status": "ok"}
- [ ] POST /api/auth/register - creates new user
- [ ] POST /api/auth/login - returns access_token
- [ ] GET /api/auth/me - returns current user (with token)
- [ ] POST /api/refresh - refreshes access token
- [ ] POST /api/parse - parses QASM-D circuit
- [ ] POST /api/execute - executes circuit (alias for parse)

## 3. Authentication Flow
- [ ] Register endpoint validates email format
- [ ] Register prevents duplicate emails
- [ ] Register hashes passwords
- [ ] Login returns JWT access_token
- [ ] Login rejects wrong passwords
- [ ] Token-protected endpoints reject missing token
- [ ] Token-protected endpoints reject invalid token

## 4. Frontend3.html
- [ ] Frontend loads at http://localhost:8000/
- [ ] Auth overlay appears when not logged in
- [ ] Can register new user from frontend
- [ ] Can login with registered credentials
- [ ] User info displays after login
- [ ] Logout button works
- [ ] Can navigate to different tabs

## 5. Circuit Parsing
- [ ] Circuit parsing accepts QASM-D string
- [ ] Returns metadata (num_qubits, depth)
- [ ] Returns visualization data (histogram, bloch, qsphere)
- [ ] Returns SDK code (qiskit, cirq, etc.)
- [ ] Handles measurement gates correctly

## 6. CORS
- [ ] CORS headers present in responses
- [ ] OPTIONS requests return 200
- [ ] Frontend can make requests to API

## 7. Error Handling
- [ ] Invalid requests return proper error messages
- [ ] Unauth requests return 401
- [ ] Validation errors return 400
- [ ] Server doesn't crash on bad input

## Issues to Fix
- [ ] TBD - will be updated after testing
