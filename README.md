================================================================================
#  Upwind Security — Home Assignment Submission
================================================================================
### Candidate: Michelle Cain | Role: Software Engineering Challenge 🚀

Welcome to my official repository submission for the Upwind Security Home Assignment. This project encompasses two main security-focused parts, transitioning from client-side mail ecosystem defenses to building an enterprise-grade, containerized secure portal architecture.

---

## 📂 Repository Structure & Navigation

The repository is divided into two distinct, standalone components:

### 🔗 [Part 1 — Gmail Add-on: Malicious Email Scorer](./part1-gmail-addon)
A security-focused Google Workspace integration that inspects incoming emails, hooks into automated detection telemetry, and provides real-time phishing risk metrics.
* 📄 **Deep-Dive Readme:** For configuration, APIs used, and limitations, visit the [Part 1 Documentation](./part1-gmail-addon/README.md).

### 🔗 [Part 2 — Secure Development: Backend Portal](./part2-backend)
A fully functional, containerized, and hardened full-stack monitoring panel featuring user management operations and a live infrastructure alert feed.
* 📄 **Deep-Dive Readme:** For fast Docker setup guides, operational endpoints, and architectural frameworks, visit the [Part 2 Documentation](./part2-backend/README.md).
* 🛡️ **Threat Modeling:** To view the security design patterns and OWASP mapping, see the [Part 2 Threat Analysis Document](./part2-backend/THREAT_ANALYSIS.md).

---

## 🎯 Executive Summary of Deliverables

### 📧 Part 1: Malicious Email Scorer
- **Core Strategy:** Developed a clean card-based UI layout utilizing Google Workspace APIs to deliver transparent security verdicts directly inside user mail views.
- **Signals Examined:** Evaluates internal email headers, parses metadata, and flags suspicious messaging characteristics to build an explainable risk score.
- **User Safety Controls:** Empowers operators with custom configuration blocks and dedicated tracking histories.

### 🔐 Part 2: Secure Development & Hardening
- **FastAPI Core Service:** Replaced an isolated, static mock frontend with an operational Python/FastAPI backend driving secure asynchronous communication loops.
- **Role-Based Access Control (RBAC):** Implemented severe role verification dependencies (`Admin`, `Analyst`, `Viewer`) guarding privileged paths on every request.
- **Cryptographic Foundations:** Applied strong `bcrypt` schemas for secure password serialization and signed `HS256` stateless JWT session flows.
- **Infrastructure Orchestration:** Leveraged multi-container Docker layers to guarantee single-command portability across deployment environments.

---

## 💡 Personal Reflections
Coming from a software engineering background, this home assignment was an incredible milestone for me. Prior to this, I had never had the opportunity to dive deep into cybersecurity architectures and defensive engineering.

Stepping into this domain was an absolute joy—I found the entire lifecycle of breaking down systems, identifying vulnerability landscapes, and implementing cryptographic guards and access layers intensely fascinating. Navigating through threat-thinking workflows taught me to treat user inputs with complete zero-trust and significantly expanded my engineering paradigm. I thoroughly enjoyed making design choices that balance seamless operational user experiences with rigorous server-side safety enforcement, and I am highly motivated to continue sharpening these exact skills as part of a forward-thinking security team.

## 🎓 Evaluation & Scope Reminder
This repository and its assets are structured cleanly to allow transparent local evaluation by the Upwind Security team. Local configuration keys (.env) and database seeds are purposefully left tracking within the testing directory spaces to minimize setup friction.

================================================================================