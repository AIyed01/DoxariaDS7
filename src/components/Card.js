import React from "react";
import "./card.css"; // fichier CSS optionnel pour le style

export const Card = ({ children, className }) => {
  return (
    <div className={`custom-card ${className || ""}`}>
      {children}
    </div>
  );
};

export const CardContent = ({ children }) => {
  return (
    <div className="card-content">
      {children}
    </div>
  );
};
