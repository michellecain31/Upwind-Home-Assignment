import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import LoginModal from "./components/LoginModal";
import WelcomeBanner from "./components/WelcomeBanner";
import EventsPage from "./pages/EventsPage";
import UsersPage from "./pages/UsersPage";
import NotFound from "./pages/NotFound";
import { getRoleFromToken } from "./api";

// Route guard: renders children only for admin users.
// Non-admins are silently redirected to /events.
function AdminRoute({ children }: { children: React.ReactNode }) {
  const isAdmin = getRoleFromToken() === "admin";
  return isAdmin ? <>{children}</> : <Navigate to="/events" replace />;
}

function App() {
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    const dismissed = sessionStorage.getItem("login-dismissed");
    const token = localStorage.getItem("token");
    if (!dismissed && !token) {
      setShowLogin(true);
    }
  }, []);

  const handleCloseLogin = () => {
    sessionStorage.setItem("login-dismissed", "true");
    setShowLogin(false);
  };

  return (
    <>
      <Navbar onLoginClick={() => setShowLogin(true)} />
      <div className="container" style={{ padding: "24px" }}>
        <WelcomeBanner />
        <Routes>
          <Route path="/" element={<Navigate to="/events" replace />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/users" element={<AdminRoute><UsersPage /></AdminRoute>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      {showLogin && <LoginModal onClose={handleCloseLogin} />}
    </>
  );
}

export default App;