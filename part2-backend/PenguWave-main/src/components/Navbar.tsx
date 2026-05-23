import { Link, useLocation, useNavigate } from "react-router-dom";
import { getRoleFromToken } from "../api";

interface NavbarProps {
  onLoginClick: () => void;
}

export default function Navbar({ onLoginClick }: NavbarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const isAdmin = getRoleFromToken() === "admin";

  const handleLogout = () => {
    // JWT logout is purely client-side: discard the token.
    // There is no /api/auth/logout endpoint — the backend is stateless.
    localStorage.removeItem("token");
    navigate("/events");
    window.location.reload();
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/events" style={{ textDecoration: "none", color: "inherit" }}>
          PenguWave 🐧
        </Link>
      </div>
      <div className="navbar-links">
        <Link
          to="/events"
          className={location.pathname.startsWith("/events") ? "active" : ""}
        >
          Events
        </Link>
        {isAdmin && (
          <Link
            to="/users"
            className={location.pathname === "/users" ? "active" : ""}
          >
            Users
          </Link>
        )}
        {token ? (
          <button onClick={handleLogout} className="navbar-login-btn" style={{ borderColor: "red", color: "red" }}>
            Logout
          </button>
        ) : (
          <button onClick={onLoginClick} className="navbar-login-btn">
            Login
          </button>
        )}
      </div>
    </nav>
  );
}