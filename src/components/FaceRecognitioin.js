import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import * as faceapi from "face-api.js"; // Import face-api.js
import { useNavigate } from "react-router-dom";
import "./FaceRecognition.css";
import "./login.css"
const FaceRecognition = (props) => {
  const webcamRef = useRef(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [capturedImage, setCapturedImage] = useState(null);
  const [recognizedName, setRecognizedName] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFaceLoading, setIsFaceLoading] = useState(false);
  const [isFaceCaptured, setIsFaceCaptured] = useState(false);
  const [isFaceVerification, setIsFaceVerification] = useState(false);
  const navigate = useNavigate();
  const emailRef = useRef("");
  const passwordRef = useRef("");
  
  // Load face-api.js models
  useEffect(() => {
    const loadModels = async () => {
      await faceapi.nets.tinyFaceDetector.loadFromUri("/models"); // Load the face detection model
      await faceapi.nets.faceLandmark68Net.loadFromUri("/models"); // Optional: Load landmark model
    };
    loadModels();
  }, []);

  // Detect faces and capture image automatically
  useEffect(() => {
    if (!isFaceVerification) return;
    const detectFaces = async () => {
      if (webcamRef.current && webcamRef.current.video) {
        const video = webcamRef.current.video;

        // Detect faces in the video stream
        const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());

        if (detections.length > 0) {
          // If a face is detected, capture the image
          const imageSrc = webcamRef.current.getScreenshot();
          setCapturedImage(imageSrc);
          sendImageToBackend(imageSrc);
        }
      }
    };

    // Run face detection every 500ms
    const interval = setInterval(detectFaces, 1000);
    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [isFaceVerification]);

  const sendImageToBackend = async (imageBase64) => {
   
    setErrorMessage("");
    setIsLoading(true);
    try {
      
      const response = await axios.post(
        "http://127.0.0.1:8000/api/user_login/",
        {
          email: emailRef.current,
          password: passwordRef.current,
          image: imageBase64,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      
      
      setRecognizedName(response.data.user);
      setErrorMessage("");
      
      if (response.data.success) {
        setTimeout(() => {
          props.handleLogin(true,response.data.user);
          // set user
          navigate("/"); // Navigate to home page
        }, 3000);
      }
      
    } catch (error) {
      
      setRecognizedName("");
      setErrorMessage("false");
    
    } finally {
      setIsLoading(false);
    }
  };

  const Login = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setIsLoading(true);

    if (!email || !password) {
      setErrorMessage("Veuillez entrer un email et un mot de passe valides.");
      return;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/user_login/",
        { email, password },
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.message === "Credentials verified. Face recognition required") {
        setIsFaceVerification(true);
        emailRef.current = email;
        passwordRef.current = password;

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
  return (
    
    <div className="login-container">
      {!isFaceVerification ? (
        <form onSubmit={Login} className="login-form">
          <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
          <h1 className="title">Welcome To Doxaria</h1>
          
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
    <div className="face-recognition-container">
      <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
      <h1 className="title">Welcome To Doxaria</h1>
      <p className="subtitle">Position your face in front of the camera to log in!</p>

      {/* Show webcam feed */}
      {recognizedName !== "false" && !recognizedName && (
        <div className="webcam-wrapper">
          <Webcam
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="webcam"
            mirrored={true}
          />
        </div>
      )}

      {/* Show captured image and success message if face is recognized */}
      {recognizedName && recognizedName !== "false" && (
        <div className="success-container">
          <img src={capturedImage} alt="Capture" className="captured-image" />
          <h3 className="result-text success">Welcome, {recognizedName}! 🎉</h3>
        </div>
      )}

      {/* Show error message if face is not recognized */}
      {errorMessage === "false" && (
        <div className="error-container">
          <h3 className="result-text error">Face Unrecognized 😔</h3>
          <p className="error">Please try again.</p>
        </div>
      )}
    </div>
  )}
    </div>
  );
};

export default FaceRecognition;