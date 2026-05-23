import { useState, useEffect } from "react";
import { User } from "../types";
import { getUsers, createUser, deleteUser } from "../api";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("analyst");

  // טעינת המשתמשים מהשרת בעת עליית העמוד
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = () => {
    setLoading(true);
    getUsers()
      .then((data) => {
        if (Array.isArray(data)) {
          setUsers(data);
          setError(null);
        } else if (data && data.error) {
          setError(data.error);
        } else {
          setError("Failed to load users");
        }
      })
      .catch((err) => {
        console.error("Error fetching users:", err);
        
        // פתרון סופי והרמטי: בדיקה אם המשתמש מחובר.
        // אם יש טוקן והגענו לפה, השרת החזיר 403 (כי הרי הלוגים מראים 403 Forbidden).
        const hasToken = !!localStorage.getItem("token");
        
        if (hasToken) {
          setError("Admin access required");
        } else {
          setError("Network error connecting to backend");
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newPassword) return;

    try {
      const result = await createUser({
        email: newEmail,
        password: newPassword,
        role: newRole,
      });

      if (result && !result.error) {
        fetchUsers(); // רענון הרשימה לאחר יצירה מוצלחת
        setNewEmail("");
        setNewPassword("");
        setNewRole("analyst");
        setShowForm(false);
      } else {
        alert(result.error || "Failed to create user");
      }
    } catch (err) {
      console.error("Error creating user:", err);
      alert("Error creating user");
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      const result = await deleteUser(id);
      if (result && !result.error) {
        fetchUsers(); // רענון הרשימה לאחר מחיקה
      } else {
        alert(result.error || "Failed to delete user");
      }
    } catch (err) {
      console.error("Error deleting user:", err);
      alert("Error deleting user");
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1>User Management (Admin Only)</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {showForm && (
        <div style={{ background: "white", padding: 16, borderRadius: 6, marginBottom: 20, border: "1px solid #ddd" }}>
          <form onSubmit={handleAddUser} style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12 }}>Email</label>
              <input type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} required />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12 }}>Password</label>
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12 }}>Role</label>
              <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
                <option value="admin">Admin</option>
                <option value="analyst">Analyst</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <button type="submit" className="btn-primary">
              Create User
            </button>
          </form>
        </div>
      )}

      {error && (
        <div style={{ color: "red", padding: 10, background: "#ffebee", borderRadius: 4, marginBottom: 16 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading ? (
        <p>Loading users...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <span style={{ color: user.status === "active" ? "green" : "#999" }}>
                    {user.status}
                  </span>
                </td>
                <td>
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      handleDelete(user.id);
                    }}
                    style={{ color: "red" }}
                  >
                    Delete
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && users.length === 0 && !error && (
        <p style={{ color: "#999" }}>No users found.</p>
      )}
    </div>
  );
}