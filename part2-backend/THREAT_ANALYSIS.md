# Threat Analysis - Part 2: PenguWave Security Operations Portal

## System Overview & Assets

PenguWave is a Security Operations Portal handling sensitive infrastructure alerts and user access controls. The main assets requiring protection are:

- **User Credentials & Session Tokens:** The identity layer of the system.
- **Security Event Logs & Alert Data:** Confidential infrastructure security alerts.
- **Administrative Capabilities:** User creation, deletion, and role modifications.

---

## Potential Threats & Attack Vectors

### 1. Authentication Failures (OWASP Top 10 - Identification and Authentication Failures)

**The Threat:**
Attackers may attempt brute-force attacks on the login endpoint to guess analyst passwords. If session management uses weak or predictable tokens, or transmits them over unencrypted networks, attackers could forge or intercept the session state to bypass the login phase entirely.

**Protection Implemented in Code:**
- **Secure Password Hashing:** Passwords are never stored in cleartext. The system hashes passwords using `bcrypt` with a unique cryptographic salt before saving them to the SQLite database.
- **Stateless JWT Sessions:** Authentication relies on signed JSON Web Tokens (JWT) using a strong secret key and the `HS256` algorithm, enforcing strict stateless session verification.
- **Production Roadmap Note:** To prevent automated credential stuffing, an operational rate-limiting layer (e.g., `slowapi` or an upstream Web Application Firewall / WAF) is designed to protect the `/api/auth/login` route in production environments.

---

### 2. Broken Access Control (OWASP Top 10 - Broken Access Control)

**The Threat:**
An unauthenticated guest or a low-privilege Analyst could try to manipulate client-side code or intercept API requests to reach administrative routes (like the user management view), allowing them to view other users' data, create malicious accounts, or elevate their own role.

**Protection Implemented in Code:**
- **Server-Side Truth:** The frontend is treated as completely untrusted. The FastAPI backend acts as the absolute source of truth.
- **Strict Role Verification (RBAC):** Privileged API endpoints (such as `GET /api/users` and `POST /api/users`) are strictly protected by server-side dependencies (`Depends(require_admin)`). The server decodes the token and checks the user's role directly against the database on **every single request**.
- **Clean Unauthorized Handling:** If a non-admin user attempts an admin action, the backend rejects the request immediately with a `403 Forbidden` status. The frontend React application catches this status and gracefully renders an `Admin access required` error block instead of exposing data.

---

### 3. Injection Attacks (OWASP Top 10 - Injection)

**The Threat:**
Malicious input supplied in the email or password fields during login or user creation could attempt an SQL Injection attack to bypass authentication, expose the database structure, or delete data.

**Protection Implemented in Code:**
- **Parameterized Queries via ORM:** The backend utilizes SQLAlchemy ORM, which completely parameterizes inputs and separates the query structure from user data, rendering classical SQL injection impossible.
- **Strict Data Schema Validation:** Input payloads are strictly validated using Pydantic schemas (`LoginRequest`, `CreateUserRequest`) before any business logic executes, dropping any malformed or unexpected attributes.

---

### 4. Data Exposure & Token Hijacking

**The Threat:**
If the frontend is targeted by Cross-Site Scripting (XSS), malicious scripts could try to intercept user data. Additionally, returning broad user objects that include internal sensitive fields like password hashes over the network poses a critical data exposure risk.

**Protection Implemented in Code:**
- **Data Filtering:** API responses explicitly use Pydantic projection models (`UserResponse`) that exclude password hashes. The backend only transmits the required metadata (`id`, `email`, `role`, `status`) to the frontend.
- **Bearer Token Management:** Session tokens are stored in the client's `LocalStorage` and transmitted securely via standard `Authorization: Bearer <token>` HTTP headers.
- **Production Roadmap Note:** To maximize defenses against sophisticated client-side XSS token-theft, the production architecture blueprint outlines a migration from `LocalStorage` to signed `HttpOnly` and `SameSite=Lax` cookies, combined with a strict Content Security Policy (CSP) header configuration.

---

## Threat & Defense Summary

| Threat Vector | Security Control Implemented in Code | Future Production Roadmap Expansion |
| :--- | :--- | :--- |
| **Brute-Force Login** | Cryptographic validation delays | Upstream Rate-Limiting / WAF integration |
| **SQL Injection** | SQLAlchemy ORM parameterized queries | Database access constraints |
| **Weak / Stolen Passwords** | One-way `bcrypt` hashing with salt | Multi-Factor Authentication (MFA) |
| **Privilege Escalation** | Server-side role validation (`Depends`) | Token revocation checklists |
| **Data Exposure** | Pydantic response filtering (No hashes sent) | Full network layer encryption |
| **Unprotected Routes** | Automated JWT validation middleware | Strict token lifetime expiration |
| **Token Theft / XSS** | Clean variable isolation & strict CORS | Migration to `HttpOnly` session cookies |