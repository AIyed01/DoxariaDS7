import './App.css';
import Home from './components/Home';
import FaceRecognition from './components/FaceRecognitioin';
import { Route, Routes, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import SuperAdminLogin from './components/SuperAdminLogin';
import Dashboard from './components/Dashboard';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [username, setUserName] = useState("");

  useEffect(() => {
    const isLoggedInStr = localStorage.getItem('isLoggedIn');
    if (isLoggedInStr === 'true') {
      setIsLoggedIn(true);
    }
    const userStr = localStorage.getItem('username');
    if (userStr) {
      setUserName(userStr);
    }
    const adminStr = localStorage.getItem('isAdmin');
    if (adminStr === 'true') {
      setIsAdmin(true);
    }
  }, []);

  const handleLogin = (loggedIn, user, admin = false) => {
    setIsLoggedIn(loggedIn);
    setIsAdmin(admin);
    setUserName(user);
    localStorage.setItem('isLoggedIn', loggedIn);
    localStorage.setItem('username', user);
    localStorage.setItem('isAdmin', admin);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsAdmin(false);
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('username');
    localStorage.removeItem('isAdmin');
  };

  return (
    <Routes>
      {/* Redirect login and admin-login to / if already logged in */}
      <Route path="/login" element={isLoggedIn ? <Navigate to="/" /> : <FaceRecognition handleLogin={handleLogin} />} />
      <Route path="/admin-login" element={isLoggedIn ? <Navigate to="/" /> : <SuperAdminLogin handleLogin={handleLogin} />} />

      {/* Show Dashboard if Admin, otherwise Home */}
      <Route path="/" element={isLoggedIn ? (isAdmin ? <Dashboard handleLogout={handleLogout} /> : <Home user={username} handleLogout={handleLogout} />) : <Navigate to="/login" />} />
    </Routes>
  );
}

export default App;
