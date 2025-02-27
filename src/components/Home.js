import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";
import { FaVolumeUp, FaUserCircle } from "react-icons/fa";
import axios from "axios";

const NavBar = ({ handleLogout }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  return (
    <div className="header">
      <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
      <div className="user-icon" onClick={() => setShowDropdown(!showDropdown)}>
        <FaUserCircle size={20} />
        <h4>Eya-Lamouri</h4>
        {showDropdown && (
          <div className="dropdown-menu">
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </div>
    </div>
  );
};

const Home = (props) => {
  const [isFraud, setIsFraud] = useState(false);
  const navigate = useNavigate();
  const [language, setLanguage] = useState("fr");
  const [translatedData, setTranslatedData] = useState(null);
  const [selectedImageName, setSelectedImageName] = useState(null);

  const Logout = () => {
    props.handleLogout();
    navigate("/login");
  };

  const data = {
    sexe: "Homme",
    age: 32,
    Doctor: "Gynecologue",
    R: [
      { date: "01/01/2025", description: "pharmacie" },
      { date: "05/01/2025", description: "G1" },
    ],
  };

  useEffect(() => {
    if (language !== "fr") {
      translateData(language);
    } else {
      setTranslatedData(null);
    }
  }, [language]);

  const translateData = async (selectedLang) => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/translate/", {
        ...data,
        language: selectedLang,
      });
      console.log("Translated Data:", response.data);
      setTranslatedData(response.data);
    } catch (error) {
      console.error("Translation error:", error);
    }
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0]; // Prendre le premier fichier sélectionné
    if (file) {
      setSelectedImageName(file.name); // Mettre à jour le nom du fichier sélectionné
    }
  };

  const displayData = translatedData || data;
  const headers = Object.keys(displayData).filter((key) => key !== "R" && key !== "language");

  const resultHeaders = displayData.R && displayData.R.length > 0 ? Object.keys(displayData.R[0]) : [];

  return (
    <div>
      <NavBar handleLogout={Logout} />
      <div className="home-container">
        <div className="upload-section">
          <p>Upload your Image.. To extract your data</p>
          <div className="upload-buttons">
            <button className="btn take-image">📷 Take Image</button>
            <label className="btn upload-document">
              ⬇ Upload Image
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                style={{ display: "none" }} // Cacher l'input file
              />
            </label>
            {selectedImageName && <span className="file-name">{selectedImageName}</span>} 
          </div>
        </div>
        <div className="data-container">
          <div className="container-row">
            <div className="data-box">
              <div className="title-select">
                <h3>Extracted Data</h3>
                <select onChange={(e) => setLanguage(e.target.value)} value={language}>
                  <option value="fr">Français</option>
                  <option value="ar">Arabe</option>
                  <option value="en">Anglais</option>
                </select>
              </div>
              <p>
                Document Type: <strong>Bulletin de soin</strong>
              </p>

              <table className="data-table">
                <thead>
                  <tr>
                    {headers.map((header, index) => (
                      <th key={index}>{header.charAt(0).toUpperCase() + header.slice(1)}</th>
                    ))}
                    {resultHeaders.map((header, index) => (
                      <th key={index + headers.length}>{header.charAt(0).toUpperCase() + header.slice(1)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayData.R && displayData.R.length > 0 ? (
                    displayData.R.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {rowIndex === 0 &&
                          headers.map((header, index) => (
                            <td key={index} rowSpan={displayData.R.length}>
                              {displayData[header]}
                            </td>
                          ))}
                        {resultHeaders.map((key, index) => (
                          <td key={index + headers.length}>{row[key]}</td>
                        ))}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={headers.length + resultHeaders.length}>Aucune donnée disponible</td>
                    </tr>
                  )}
                </tbody>
              </table>

              {isFraud && <p className="fraud-detection">⚠ Fraud detection: A male cannot visit a gynecologist.</p>}
            </div>
            <div className="icons-container">
              <FaVolumeUp className="icon" title="Lire à haute voix" />
            </div>
          </div>
        </div>
        <footer className="footer">By: DataWizards</footer>
      </div>
    </div>
  );
};

export default Home;
