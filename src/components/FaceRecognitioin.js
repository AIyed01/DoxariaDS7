import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import * as faceapi from "face-api.js"; // Import face-api.js
import { useNavigate } from "react-router-dom";
import "./FaceRecognition.css";

const FaceRecognition = (props) => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [recognizedName, setRecognizedName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

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
    const interval = setInterval(detectFaces, 500);
    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  const sendImageToBackend = async (imageBase64) => {
    setIsLoading(true);
    try {
      setErrorMessage("");
      const response = await axios.post("http://127.0.0.1:8000/api/recognize-face/", {
        image: imageBase64,
      });

      console.log("✅ Réponse du serveur :", response.data);
      setRecognizedName(response.data.recognized);


      // If face is recognized, navigate to home page after 3 seconds
      if (response.data.recognized !== "false") {
        setTimeout(() => {
          props.handleLogin(true,response.data.recognized);
          // set user
          navigate("/"); // Navigate to home page
        }, 3000);
      }
      if (response.data.recognized === "false") {
        setRecognizedName("");
        setErrorMessage("false");
      }
    } catch (error) {
      console.error("❌ Erreur lors de l'envoi de l'image :", error);
      setRecognizedName("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    
    <div className="loginPage">
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
    </div>
  );
};

export default FaceRecognition;