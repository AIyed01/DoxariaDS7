import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { FiUserPlus, FiLogOut, FiTrash2 } from "react-icons/fi";
import { FaUsers, FaChartBar } from "react-icons/fa";
import "./AdminDashboard.css";
import { useNavigate } from "react-router-dom";
import axios from 'axios';

import { loadModels, validateFace } from '../utils/faceDetection';
import Statistics from "./Statistics";

const data = [
  { name: "Jan", users: 40 },
  { name: "Feb", users: 55 },
  { name: "Mar", users: 30 },
  { name: "Apr", users: 80 },
  { name: "May", users: 50 },
];

const Dashboard = ({ handleLogout }) => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState("dashboard");
  const [userData, setUserData] = useState({ email: "", password: "", image: null, imageName: "" });
  const [showImagePopup, setShowImagePopup] = useState(false);
  const [tempImage, setTempImage] = useState(null);
  const [tempImageName, setTempImageName] = useState("");
  const [users, setUsers] = useState([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [successMessage, setSuccessMessage]= useState("");
  const [imageNameError, setImageNameError] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogoutClick = () => {
    handleLogout();
    navigate("/admin-login");
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData({ ...userData, [name]: value });
  };

  const handleFileChange = async (e) => {
    setErrorMessage("");
    const file = e.target.files[0];
    if (!file) return;
  
    // Create image element for face detection
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
  
    img.onload = async () => {
      try {
        // Validate face
        const { isValid, faceCount } = await validateFace(img);
        
        if (!isValid) {
          setErrorMessage(
            faceCount === 0 
              ? "No face detected. Please upload a clear face image." 
              : "Multiple faces detected. Upload an image with exactly one face."
          );
          return;
        }
  
        // Proceed if valid
        setTempImage(URL.createObjectURL(file));
        const fileName = file.name;
        const lastDot = fileName.lastIndexOf('.');
        setTempImageName(fileName.substring(0, lastDot));
        setUserData(prev => ({
          ...prev,
          imageExtension: fileName.substring(lastDot)
        }));
        setShowImagePopup(true);
        
      } catch (error) {
        setErrorMessage("Face detection failed. Please try another image.");
      }
    };
  };
  useEffect(() => {
    // Load face detection models on component mount
    loadModels().catch(console.error);
  }, []);

  const handleVerifyImageName = () => {
    if (!tempImageName.trim()) {
      setImageNameError("Please enter a valid name");
      return;
    }
  
    // Check for duplicate names (including extension)
    const fullName = `${tempImageName}${userData.imageExtension}`;
    const isDuplicate = users.some(user => {
      if (!user.image) return false;
      const userImageName = user.image.split('/').pop();
      return userImageName === fullName;
    });
  
    if (isDuplicate) {
      setImageNameError("This image name is already in use");
      return;
    }
  
    setImageNameError("");
    setUserData(prev => ({
      ...prev,
      image: tempImage,
      imageName: tempImageName,
      // Keep the original extension
      finalImageName: fullName
    }));
    setShowImagePopup(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    if (!userData.email || !userData.password) {
      setErrorMessage("Email and password are required");
      return;
    }
    try {
      const formData = new FormData();
      formData.append('email', userData.email);
      formData.append('password', userData.password);
      
      if (userData.image) {
        const response = await fetch(userData.image);
        const blob = await response.blob();
        formData.append('image', blob, userData.finalImageName);
      }
  
      const response = await axios.post('http://localhost:8000/api/users/', formData);
      setSuccessMessage('User created successfully!');
      setUserData({ email: "", password: "", image: null, imageName: "" });
      setTempImage(null);
      setTempImageName("");
      setSelectedTab("users");
      setSuccessMessage("");
    } catch (error) {
      if (error.response?.data?.email) {
        setErrorMessage(`Email error: ${error.response.data.email}`);
      } else if (error.response?.data?.image) {
        setErrorMessage(`Image error: ${error.response.data.image}`);
      } else {
        setErrorMessage('Error creating user. Please try again.');
      }
    }
  };

  useEffect(() => {
    if (selectedTab === "users") {
      fetchUsers();
    }
  }, [selectedTab]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/users/list/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const confirmDelete = (userId) => {
  setUserToDelete(users.find(user => user.id === userId));
  setShowDeleteConfirm(true);
};

const handleDelete = async () => {
  if (!userToDelete) return;
  
  try {
    await axios.delete(`http://localhost:8000/api/users/delete/${userToDelete.id}/`);
    setUsers(users.filter(user => user.id !== userToDelete.id));
    setShowDeleteConfirm(false);
  } catch (error) {
    console.error('Error deleting user:', error);
    alert(`Failed to delete user: ${error.response?.data?.detail || error.message}`);
  }
};

  const getImageName = (imagePath) => {
    if (!imagePath) return 'No image';
    const filename = imagePath.split('/').pop();
    return filename.split('.').slice(0, -1).join('.');
  };

  return (
    <div className="admin-container">
      <div className="sidebar">
        <div className="logo"><img src="/DoxLogo.png" alt="Dox Logo" /></div>
        <nav className="nav-links">
          <button className={`nav-item ${selectedTab === "dashboard" ? "active" : ""}`} onClick={() => setSelectedTab("dashboard")}>
            <FaChartBar /> Dashboard
          </button>
          <button className={`nav-item ${selectedTab === "users" ? "active" : ""}`} onClick={() => setSelectedTab("users")}>
            <FaUsers /> Users
          </button>
          <button className={`nav-item ${selectedTab === "add-user" ? "active" : ""}`} onClick={() => setSelectedTab("add-user")}>
            <FiUserPlus /> Add User
          </button>
        </nav>
        <button className="logout-btn" onClick={handleLogoutClick}> <FiLogOut /> Logout</button>
      </div>

      <div className="main-content">
        {selectedTab === "dashboard" && (
          
          <Statistics/>
        )}

         {selectedTab === "users" && (
            <div>
              <h2>User Management</h2>
              <div className="user-list">
                {users.map(user => (
          <div key={user.id} className="user-card">
            <div className="user-image-container">
              {user.image ? (
                <>
                  <img 
                    src={`${user.image}?${new Date().getTime()}`}
                    alt={user.email}
                    className="user-image"
                    onError={(e) => {
                      e.target.onerror = null; 
                      e.target.src = '/placeholder-user.png';
                    }}
                  />
                  <p className="image-name">{getImageName(user.image)}</p>
                </>
              ) : (
                <div className="no-image-placeholder">
                  <span>No Image</span>
                </div>
              )}
            </div>
            
            <div className="user-details">
              <p><strong>Email:</strong> {user.email}</p>
            </div>
            
            <button 
              onClick={() => confirmDelete(user.id)}
              className="delete-btn"
              aria-label="Delete user"
            >
              <FiTrash2 />
            </button>
          </div>
        ))}
              </div>
            </div>
          )}

{showDeleteConfirm && <div className="overlay"></div>}
{showDeleteConfirm && (
  <div className="delete-popup">
    <div className="popup-content">
      <h3>Confirm Deletion</h3>
      <p>Are you sure you want to delete user:</p>
      {userToDelete?.image && (
        <div className="confirmation-image">
          <img 
            src={userToDelete.image} 
            alt="User to delete" 
            className="image-preview"
          />
          <p className="image-name">{getImageName(userToDelete.image)}</p>
        </div>
      )}
      <p><strong>Email:</strong> {userToDelete?.email}</p>
      <div className="popup-buttons">
        <button 
          onClick={() => setShowDeleteConfirm(false)}
          className="cancel-btn"
        >
          Cancel
        </button>
        <button 
          onClick={handleDelete}
          className="confirm-delete-btn"
        >
          Delete
        </button>
      </div>
    </div>
  </div>
)}




        {selectedTab === "add-user" && (
          <div>
            <h2>Add User</h2>
            <div className="container"> 
            <form className="form-container" >
              <input type="email" name="email" placeholder="Email" className="input-field" value={userData.email} onChange={handleInputChange} required />
              <input type="password" name="password" placeholder="Password" className="input-field" value={userData.password} onChange={handleInputChange} required />
              <label className="file-label" htmlFor="fileInput">Choose Image</label>
              <input type="file" id="fileInput" accept="image/*" className="file-input" onChange={handleFileChange} capture="user" />
              {errorMessage && <div className="error-message">{errorMessage}</div>}
            </form>
            <div className="img-side">
            {tempImage && <img src={tempImage} alt="Selected" className="image-preview" />}
            {userData.imageName && <p className="verified-image-name">{userData.imageName}</p>}

            </div>
            
          </div>
          
          <button onClick={handleSubmit} className="submit-btn">Add User</button>
          {successMessage && <div className="successMessage"> <p>{successMessage}</p></div>}
          </div>
        )}
      </div>
      {showImagePopup && (
        <>
        {/* Black transparent overlay */}
        <div 
          className="overlay" 
          onClick={() => {}} // Empty function prevents closing when clicking outside
        />
        <div className="image-popup">
          <div className="popup-content">
            <p>Modify image name to be like firstname-lastname:</p>
            {tempImage && <img src={tempImage} alt="Selected" className="image-preview" />}
            
            <div className="name-input-container">
              <input
                type="text"
                value={tempImageName}
                onChange={(e) => setTempImageName(e.target.value)}
                className="image-name-input"
              />
              <span className="extension-display">
                {userData.imageExtension}
              </span>
            </div>
            
            {imageNameError && <p className="error-message">{imageNameError}</p>}
            <button onClick={handleVerifyImageName} className="verify-btn">
              Verify
            </button>
          </div>
        </div>
        </>
)}
    </div>
  );
};

export default Dashboard;
