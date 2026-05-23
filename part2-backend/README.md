================================================================================
# 🐧 PenguWave — Security Operations Portal
================================================================================
Official submission for the Upwind Security assessment (Part 2 - Secure Development) 

## Technologies Used
This project implements a secure full-stack Security Operations Portal featuring:
- React
- TypeScript
- FastAPI
- Python
- SQLite
- SQLAlchemy
- JWT Authentication
- Docker
- Docker Compose
- bcrypt

--------------------------------------------------------------------------------
📂 PROJECT STRUCTURE
--------------------------------------------------------------------------------

```text
part2-backend/
│
├── backend/
│   ├── main.py                # FastAPI application entry point
│   ├── database.py            # Database connection and initialization
│   ├── models.py              # SQLAlchemy database models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── auth.py                # JWT authentication & password hashing
│   ├── requirements.txt       # Python dependencies
│   └── database.db            # Local SQLite database file
│
├── PenguWave-main/
│   ├── data/
│   │   └── mock_events.json   # Mock security events dataset
│   │
│   ├── src/
│   │   ├── api.ts             # Centralized API communication layer
│   │   ├── App.tsx            # Main application routing/layout
│   │   ├── pages/             # Main application views
│   │   └── components/        # Reusable UI components
│   │
│   ├── public/                # Static public frontend assets
│   ├── dist/                  # Production frontend build output
│   ├── docs/                  # Additional project documentation
│   ├── package.json           # Node.js project configuration
│   ├── package-lock.json      # Locked dependency versions
│   ├── vite.config.ts         # Vite frontend build configuration
│   ├── Dockerfile             # Frontend container definition
│   └── nginx.conf             # Nginx reverse proxy configuration
│
├── docker-compose.yml         # Multi-container orchestration
├── README.md                  # Project documentation
├── THREAT_ANALYSIS.md         # Security threat analysis
└── .env                       # Environment variables (ignored in production)
```
--------------------------------------------------------------------------------
 HOW TO RUN THE PROJECT
--------------------------------------------------------------------------------

# 🐳 OPTION A — Docker Compose (Recommended)


Clean up potential volume caches and containers from previous runs
```bash
docker compose down -v
```
Build, recreate, and launch the portal cleanly in background mode
```bash
docker compose up --build --force-recreate -d
```

Application URLs:

🔗 Frontend Gateway:
```text
http://localhost
``` 


🔗 Backend API Instance:
```text
http://localhost:3001
``` 


# ⚙️ OPTION B — Local Setup (Manual Execution)

# 1. Run the Backend Service 🛠️
```bash
cd backend
python -m venv venv
```
On Windows:
```bash
venv\Scripts\activate
```
On Mac/Linux:
```bash
source venv/bin/activate
```
Install third-party packages and execute the server instance
```bash
pip install -r requirements.txt
python main.py
```

Backend Local Link:
```text
http://localhost:3001 🔗
``` 


On its initial runtime boot, the backend layer automatically instantiates:
- A local persistent SQLite database binary (`database.db`)
- Structural schema data tables
- Pre-populated test data models

--------------------------------------------------------------------------------

# 2. Run the Frontend UI 🎨
```bash
cd PenguWave-main
npm install
npm run dev
```


Frontend Local Link:
```text
http://localhost:5173 🔗
``` 


--------------------------------------------------------------------------------
👥 DEMO USERS
--------------------------------------------------------------------------------

 Admin Account (Full read/write permissions):
```text
Email: admin@penguwave.io
Password: admin123
``` 


 Analyst Account (Restricted monitoring permissions):
```text
Email: analyst@penguwave.io
Password: pass456
``` 


 Viewer Account (Simulated locked out target):
```text
Email: viewer@penguwave.io
Password: view789
Status: Disabled
``` 


--------------------------------------------------------------------------------
🔐 AUTHENTICATION FLOW
--------------------------------------------------------------------------------

Identity verification follows this logical runtime path:

1. User submits an email and password pair inside the modal form interface.
2. The server tier extracts records and matches cleartext via safe bcrypt routines.
3. Upon validation check success, the system signs a stateless JWT token.
4. Client application variables trap this payload string inside LocalStorage.
5. Secure traffic headers append state keys inside subsequent requests:

   Authorization: Bearer <token>

6. The backend system decodes and evaluates the cryptographic signature on every call.

⚠️ JWT session strings are hardcapped to expire automatically after 1 hour.

--------------------------------------------------------------------------------
🛡️ AUTHORIZATION (RBAC)
--------------------------------------------------------------------------------

Access permissions are strictly enforced on the server side using an RBAC model.

🟢 Admin Role:
- Full permissions to access security telemetry event feeds.
- Full access to User Management control pathways.
- Authorized to create new analyst profiles.
- Authorized to drop user profiles (cannot drop self account state).

🟡 Non-Admin Roles (Analyst / Viewer):
- Limited to viewing read-only event parameters.
- Expressly blocked from reaching user management data layers.

Server Rejection Mapping:
- 401 Unauthorized -> Call made without a valid or attached token string.
- 403 Forbidden    -> Token is valid, but current account role lacks privileges.

💡 Client Note: The React UI explicitly drops the visible Users tab for analysts.

--------------------------------------------------------------------------------
🌐 API ENDPOINTS
--------------------------------------------------------------------------------

 Authentication Pathway:
```text
POST   /api/auth/login
``` 


 Events Architecture Pathways:
```text
GET    /api/events
``` 


 User Management Patterns:
```text
GET    /api/users
POST   /api/users
DELETE /api/users/{user_id}
``` 


 System State Pathway:
```text
GET    /api/health
``` 


--------------------------------------------------------------------------------
📊 EVENTS DATA
--------------------------------------------------------------------------------

Security incident tracking attributes are parsed out of local data files:
```text
`mock_events.json`
``` 


Anonymous public queries are discarded; only active authenticated tokens can pass.

--------------------------------------------------------------------------------
💾 STORAGE & PRIVACY
--------------------------------------------------------------------------------

The service layer state machine utilizes:
- SQLite persistent databases
- Parameterized safe interactions via SQLAlchemy ORM mappings

Raw plain text strings are never committed to disk spaces.
Stored columns keep metadata parameters filtered to:
- Securely salted password hashes (Bcrypt)
- Designated access scopes (roles)
- Account lifecycles statuses (active/disabled)

--------------------------------------------------------------------------------
🏗️ PRODUCTION SECURITY CONSIDERATIONS
--------------------------------------------------------------------------------

Moving this solution stack out of basic testing into enterprise boundaries requires:
- Restricting network paths to enforce full HTTPS/TLS transport rules.
- Transitioning LocalStorage token hooks over to signed HttpOnly secure cookies.
- Upgrading the SQLite disk files over to engine architectures like PostgreSQL.
- Eliminating local configuration hardcoding via Cloud Secret Management utilities.
- Imposing strict route rate-limiting layers to blunt automated brute force loops.
- Interfacing infrastructure logs out to central SIEM pipelines.
- Deploying systems securely behind production reverse proxy gateways (Nginx).
- Restricting raw database exposure to tightly closed isolated Private Subnets.

--------------------------------------------------------------------------------
📝 DEVELOPMENT NOTES
--------------------------------------------------------------------------------

This software package is optimized for assessment and demonstration purposes.

Local environment parameters (.env) and pre-seeded SQLite configurations are explicitly 
left available inside the file paths to allow evaluators to immediately stand up the 
project. 

In real deployment scenarios:
- Environment parameter templates are blocked from git tracking (.gitignore entries).
- Secrets are dynamically injected into active environments at process execution time.


================================================================================