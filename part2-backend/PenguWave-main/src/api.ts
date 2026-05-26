// Frontend API Client: Manages authentication caching, client-side JWT parsing, and HTTP requests to backend endpoints.

// Empty string sets context to "same origin" for Nginx proxy routing. Use "http://localhost:3001" for local host testing.
const API_URL = "";

// Decodes stateful client identity context directly from stored token payloads
export function getRoleFromToken(): string | null {
  const token = localStorage.getItem("token");
  if (!token) return null;
  try {
    const payloadBase64 = token.split(".")[1];
    const padded = payloadBase64.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(padded);
    const payload = JSON.parse(json);
    return payload.role ?? null;
  } catch {
    return null;
  }
}

// Global response interceptor utility enforcing standard error-handling bounds
async function handleResponse(res: Response) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail || errorData.error || `Request failed with status ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

// Dispatches authentication credentials and caches returned authorization token materials
export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await handleResponse(res);
  localStorage.setItem("token", data.token);
  return data;
}

// Fetches structural monitoring incident telemetry passing standard token proofs
export async function getEvents() {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("NOT_AUTHENTICATED");
  }
  const res = await fetch(`${API_URL}/api/events`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res);
}

// Fetches administrative user registry records
export async function getUsers() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res);
}

// Provisions new identity contexts under administrative role controls
export async function createUser(user: { email: string; password: string; role: string }) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(user),
  });
  return handleResponse(res);
}

// De-provisions identity profiles matching a target resource ID
export async function deleteUser(id: string) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return handleResponse(res);
}