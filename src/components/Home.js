import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";
import { FaVolumeUp } from "react-icons/fa";
import axios from "axios";

const NavBar = ({ handleLogout, user }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  return (
    <div className="header">
      <img src="/DoxLogo.png" alt="Dox Logo" className="logo" />
      <div className="user-icon" onClick={() => setShowDropdown(!showDropdown)}>
        <h4>{user}</h4>
        {showDropdown && (
          <div className="dropdown-menu">
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </div>
    </div>
  );
};

const EditableCell = ({ value, onChange }) => {
  const [editing, setEditing] = useState(false);
  const [currentValue, setCurrentValue] = useState(value);

  const handleBlur = () => {
    setEditing(false);
    onChange(currentValue);
  };

  return editing ? (
    <input
      autoFocus
      value={currentValue}
      onChange={(e) => setCurrentValue(e.target.value)}
      onBlur={handleBlur}
      onKeyDown={(e) => {
        if (e.key === "Enter") handleBlur();
      }}
    />
  ) : (
    <span onClick={() => setEditing(true)}>{currentValue}</span>
  );
};

const Home = (props) => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState("fr");
  const [data, setData] = useState({
    sexe: "Homme",
    age: 32,
    Medecin: "Gynecologue",
    R: [
      { date: "01/01/2025", description: "pharmacie" },
      { date: "05/01/2025", description: "G1" },
    ],
  });
  const [translatedData, setTranslatedData] = useState(null);
  const [selectedImageName, setSelectedImageName] = useState(null);
  const [documentType, setDocumentType] = useState(null);
  const [user] = useState(() => JSON.parse(localStorage.getItem("user")) || null);
  const [loadingTranslation, setLoadingTranslation] = useState(false);

  const Logout = () => {
    props.handleLogout();
    navigate("/login");
  }; 

  useEffect(() => {
    if (language !== "fr") {
      translateData(language);
    } else {
      setTranslatedData(null);
    }
  }, [language]);

  const translateData = async (selectedLang) => {
    setLoadingTranslation(true); // Début du chargement
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/translate/", {
        ...data,
        language: selectedLang,
      });
      setTranslatedData(response.data);
      console.log("Translated data:", response.data);
    } catch (error) {
      console.error("Translation error:", error);
    } finally {
      setLoadingTranslation(false); // Fin du chargement
    }
  };
  

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImageName(file.name);
      const formData = new FormData();
      formData.append("image", file);

      try {
        const response = await axios.post("http://127.0.0.1:8000/api/classify/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setDocumentType(response.data.label);
        setData(response.data.data || {});
      } catch (error) {
        console.error("Erreur lors de l'envoi de l'image:", error);
      }
    }
  };

  const readTableContent = async () => {
    const textToRead = JSON.stringify(data);
    try {
      await axios.post("http://127.0.0.1:8000/api/text-to-speech/", {
        phrase: textToRead,
        language,
      });
    } catch (error) {
      console.error("Erreur lors de la lecture du texte :", error);
    }
  };

  const handleEdit = (key, value, parentKey = null, index = null) => {
    const updated = { ...data };
    if (parentKey && Array.isArray(data[parentKey])) {
      updated[parentKey][index][key] = value;
    } else {
      updated[key] = value;
    }
    setData(updated);
  };

  const displayData = translatedData || data;

  return (
    
    <div>
      <NavBar handleLogout={Logout} user={props.user} />
      <div className="home-container">
        <div className="upload-section">
          <p>Upload your Image... To extract your data</p>
          <div className="upload-buttons">
            <label className="btn upload-document">
              ⬇ Upload Image
              <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: "none" }} />
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
              {documentType && (
                <p>
                  Document Type: <strong>{documentType}</strong>
                </p>
              )}
              {loadingTranslation? (
                <div className="spinner-container">
                  <div className="spinner"></div>
                </div>) : ( 
              <table className="structured-table">
  <thead>
    <tr>
      {Object.entries(displayData).map(([key, value]) => {
        if (Array.isArray(value) && typeof value[0] === "object") {
          return value[0] &&
            Object.keys(value[0]).map((subKey) => (
              <th key={`${key}-${subKey}`}>{`${key}.${subKey}`}</th>
            ));
        } else {
          return <th key={key}>{key}</th>;
        }
      })}
    </tr>
  </thead>
  <tbody key={language + JSON.stringify(displayData)}> {/* FORCE RE-RENDER */}
    <tr>
      {Object.entries(displayData).map(([key, value]) => {
        if (Array.isArray(value) && typeof value[0] === "object") {
          return value[0] &&
            Object.keys(value[0]).map((subKey) => (
              <td key={`${key}-${subKey}`}>
                {value.map((item, i) => (
                  <div key={`${key}-${subKey}-${i}`}>
                    <EditableCell
                      value={item[subKey]}
                      onChange={(val) => handleEdit(subKey, val, key, i)}
                    />
                  </div>
                ))}
              </td>
            ));
        } else {
          return (
            <td key={key}>
              <EditableCell value={value} onChange={(val) => handleEdit(key, val)} />
            </td>
          );
        }
      })}
    </tr>
  </tbody>
</table>)}

            </div>
            <div className="icons-container">
              <FaVolumeUp className="icon" title="Lire à haute voix" onClick={readTableContent} />
            </div>
          </div>
        </div>
        <footer className="footer">By: DataWizards</footer>
      </div>
    </div>
  );
};

export default Home;
