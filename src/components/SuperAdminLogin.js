import React, { useState, useRef } from "react";
import axios from "axios";
import Webcam from "react-webcam";
import "./login.css";
import { useNavigate } from "react-router-dom";
const SuperAdminLogin = (props) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isFaceVerification, setIsFaceVerification] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [recognizedName, setRecognizedName] = useState(null);
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFaceLoading, setIsFaceLoading] = useState(false);
  
  // 🔹 Étape 1 : Vérification Email + Password
  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setIsLoading(true);

    if (!email || !password) {
      setErrorMessage("Veuillez entrer un email et un mot de passe valides.");
      return;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/admin-login/",
        { email, password },
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.message === "Credentials verified. Face recognition required") {
        setIsFaceVerification(true);
      } else {
        setErrorMessage("Unexpected response from server");
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setErrorMessage("Email ou mot de passe incorrect !");
      } else {
        setErrorMessage("Erreur de connexion au serveur.");
      }
    }finally {
      setIsLoading(false);
    }
  };

  // 🔹 Étape 2 : Capture de l'image et envoi au backend
  const captureImage = async () => {
    setIsFaceLoading(true);
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setErrorMessage("");
  
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/admin-login/",
        { 
          email, 
          password, 
          image: imageSrc 
        },
        { headers: { "Content-Type": "application/json" } }
      );
  
      if (response.data.success) {
        // Successful face recognition
        
        setRecognizedName(response.data.user);
        setTimeout(()=>{
          props.handleLogin(true, "ADMIN", true); // Assuming your backend returns "ADMIN"
          navigate("/");
        },3000)
        
      } else if (response.data.error) {
        setErrorMessage(response.data.error);
        setCapturedImage(null);
      }
    } catch (error) {
      setErrorMessage(
        error.response?.data?.error || 
        "Face verification failed. Please try again."
      );
      setCapturedImage(null);
    }finally {
      setIsFaceLoading(false);
    }
  };
  return (
    <div className="login-container">
      
      {!isFaceVerification ? (
        <form onSubmit={handleLogin} className="login-form">
          <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
          <h2>Super Admin Login</h2>
          
          
          
          <input
            type="text"
            placeholder="Username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <button 
            type="submit" 
            className="btn"
            disabled={isLoading}
          >
            {isLoading ? "Verifying..." : "Login"}
          </button>

          
          {errorMessage && <p className="error-message">{errorMessage}</p>}
        </form>
      ) : (
        <div className="face-verification-container">
          <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
          <h2 className="title">Facial Verification</h2>
          
          
          
          {!recognizedName ? (<>
            <div className="webcam-wrapper">
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="webcam"
                mirrored={true}
              />
              
            </div>
            <div>
            <button 
            onClick={captureImage} 
            className="btn"
            disabled={isFaceLoading}
          >
            {isFaceLoading ? "Processing..." : "Verify"}
          </button>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
          </div></>
          ) : (
            <div className="success-container">
              <img src={capturedImage} alt="Capture" className="captured-image" />
              <h3 className="success-message">Welcome, {recognizedName}! 🎉</h3>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SuperAdminLogin;
