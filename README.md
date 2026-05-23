================================================================================
#  Upwind Security — Home Assignment Submission
<img src="https://storage.googleapis.com/clean-finder-353810/$6NcygC31Z3nl7RyK7Bk7Z975h3qeCgnEGRopO9DlGwJBtDgZatyk3h.png" width="50%" alt="System Architecture Diagram">
### Candidate: Michelle Cain | Role: Software Engineering Challenge 🚀
================================================================================


Welcome to my official repository submission for the Upwind Security Home Assignment. This project encompasses two main security-focused parts, transitioning from client-side mail ecosystem defenses to building an enterprise-grade, containerized secure portal architecture.

This repository contains a two-part security implementation : 
```text
Upwind-Home-Assignment/
├── README.md              # Global Infrastructure & Core Security Strategy
├── part1-gmail-addon/     # Client-Side Telemetry Hook & Risk Scoring
│   └── README.md          # Ecosystem Configuration & API Integration Boundaries
└── part2-backend/         # Containerized Portal & Identity Enforcement Layer
    ├── README.md          # Multi-Service Orchestration & Local Initialization
    └── THREAT_ANALYSIS.md # STRIDE/OWASP Risk Mapping & Mitigation Frameworks
```
---

##  Repository Structure & Navigation

* Part 1 — Gmail Add-on: Malicious Email Scorer (./part1-gmail-addon)
  An endpoint analysis layer leveraging Google Workspace APIs to isolate, parse, and evaluate inbound messaging anomalies. For deployment guidelines and metadata evaluation scopes, review the Subsystem Part 1 Documentation.

* Part 2 — Secure Development: Analyst Portal Backend (./part2-backend)
  A fully functional, decoupled backend architecture driving role-restricted monitoring dashboards and live network alerts. For environment management and single-command local orchestration parameters, review the Subsystem Part 2 Documentation.

* Defensive Blueprint & Risk Modeling (./part2-backend/THREAT_ANALYSIS.md)
  A dedicated threat model tracking authorization boundaries, structural input vectors, authentication lifecycles, and backend mitigation assumptions.

---

##  Executive Summary of Deliverables

### Part 1: Malicious Email Scorer
- **Core Strategy:** Developed a clean card-based UI layout utilizing Google Workspace APIs to deliver transparent security verdicts directly inside user mail views.
- **Signals Examined:** Evaluates internal email headers, parses metadata, and flags suspicious messaging characteristics to build an explainable risk score.
- **User Safety Controls:** Empowers operators with custom configuration blocks and dedicated tracking histories.

### Part 2: Secure Development & Hardening
- **FastAPI Core Service:** Replaced an isolated, static mock frontend with an operational Python/FastAPI backend driving secure asynchronous communication loops.
- **Role-Based Access Control (RBAC):** Implemented severe role verification dependencies (`Admin`, `Analyst`, `Viewer`) guarding privileged paths on every request.
- **Cryptographic Foundations:** Applied strong `bcrypt` schemas for secure password serialization and signed `HS256` stateless JWT session flows.
- **Infrastructure Orchestration:** Leveraged multi-container Docker layers to guarantee single-command portability across deployment environments.

---

##  Personal Reflections
Coming from a software engineering background, this home assignment was an incredible milestone for me. Prior to this, I had never had the opportunity to dive deep into cybersecurity architectures and defensive engineering.

Stepping into this domain was an absolute joy—I found the entire lifecycle of breaking down systems, identifying vulnerability landscapes, and implementing cryptographic guards and access layers intensely fascinating. Navigating through threat-thinking workflows taught me to treat user inputs with complete zero-trust and significantly expanded my engineering paradigm. I thoroughly enjoyed making design choices that balance seamless operational user experiences with rigorous server-side safety enforcement, and I am highly motivated to continue sharpening these exact skills as part of a forward-thinking security team.



================================================================================