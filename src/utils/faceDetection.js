// utils/faceDetection.js
import * as faceapi from 'face-api.js';

// Load models (call this once when your app starts)
export async function loadModels() {
  await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
  // Add more models if needed (landmarks, recognition)
}

// Detect if image has exactly one face
export async function validateFace(image) {
  const detections = await faceapi.detectAllFaces(
    image, 
    new faceapi.TinyFaceDetectorOptions()
  );
  
  return {
    isValid: detections.length === 1, // Exactly one face
    faceCount: detections.length
  };
}