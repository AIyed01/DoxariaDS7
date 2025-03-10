import React from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = ({ handleLogout }) => {
  const navigate = useNavigate();

  const handleLogoutClick = () => {
    handleLogout(); 
    navigate("/admin-login");
  };

  return (
    <div>
      <h1>Welcome Admin!</h1>
      <button onClick={handleLogoutClick}>Logout</button>
    </div>
  );
};

export default Dashboard;
