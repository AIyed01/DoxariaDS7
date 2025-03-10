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

  // 🔹 Étape 1 : Vérification Email + Password
  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMessage("");

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

      if (response.status === 200) {
        setIsFaceVerification(true); // Passer à la reconnaissance faciale
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setErrorMessage("Email ou mot de passe incorrect !");
      } else {
        setErrorMessage("Erreur de connexion au serveur.");
      }
    }
  };

  // 🔹 Étape 2 : Capture de l'image et envoi au backend
  const captureImage = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setErrorMessage(""); // Effacer les erreurs précédentes

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/admin-login/",
        { email, password, image: imageSrc },
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.status === 200) {
        if (response.data.recognized && response.data.recognized !== "false") { 
          setRecognizedName(response.data.recognized); 
          setTimeout(() => {  
          props.handleLogin(true,response.data.recognized,true)
            // set user
            navigate("/"); // Navigate to home page
          }, 3000);
        } else {
          setErrorMessage("Visage non reconnu 😔. Veuillez réessayer.");
          setCapturedImage(null); // Permet de réessayer
        }
      }
    } catch (error) {
      setErrorMessage("Unreconnized Face.");
    }
  };

  return (
    <div className="login-container">
      
      {!isFaceVerification ? (
        <form onSubmit={handleLogin} className="login-form">
          <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
          <h2>Super Admin Login</h2>
          
          
          
          <input
            type="email"
            placeholder="Email"
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
          
          <button type="submit" className="btn">Login</button>
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
            <button onClick={captureImage} className="btn">Verify</button>
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
