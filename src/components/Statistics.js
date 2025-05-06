// src/components/Statistics.js
import { useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, CartesianGrid } from "recharts";
import { FiUserPlus, FiLogOut } from "react-icons/fi";
import { FaUsers, FaFileAlt, FaClinicMedical, FaPills, FaCalendarDay } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "./Card.js";
import {AiOutlineCalendar } from "react-icons/ai";
import "./Statistics.css";
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#0EA5E9", "#22C55E", "#EAB308", "#EF4444"];

const documentTypeStats = [
  { name: "Medical Care", value: 450 },
  { name: "Prescription", value: 320 },
  { name: "Other", value: 430 },
];

const donutData = [
  { name: "Consultation", value: 150 },
  { name: "Analyse", value: 250 },
  { name: "Radio", value: 180 },
  { name: "Chirurgie", value: 170 },
];

const barData = [
  { name: "Jan 2024", documents: 120 },
  { name: "Feb 2024", documents: 160 },
  { name: "Mar 2024", documents: 110 },
  { name: "Apr 2024", documents: 200 },
];

const lineData = [
  { month: "Jan 2024", remboursement: 80 },
  { month: "Feb 2024", remboursement: 89 },
  { month: "Mar 2024", remboursement: 75 },
  { month: "Apr 2024", remboursement: 200 },
  { month: "Mai 2024", remboursement: 10},
  { month: "Jun 2024", remboursement: 20 },
  { month: "Jul 2024", remboursement: 20 },
  { month: "Aout 2024", remboursement: 40 },
  { month: "Sep 2024", remboursement: 50 },
  { month: "Oct 2024", remboursement: 90 },
  { month: "Nov 2024", remboursement: 110 },
  { month: "Dec 2024", remboursement: 130 },
];

const stackedData = [
  { name: "User1", "scanned medical care": 30, "scanned prescription": 10 },
  { name: "User2", "scanned medical care": 50, "scanned prescription": 15 },
  { name: "User3", "scanned medical care": 40, "scanned prescription": 20 },
  { name: "User4", "scanned medical care": 35, "scanned prescription": 25 },
];

const Statistics = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);

  const renderPage1 = () => (
    <>
      <h2>Dashboard</h2>
      <div className="stats-grid">
              <div className="stat-card gradient-blue">
                <div className="icon-box">
                <FaFileAlt />
                </div>
                <div className="stat-info">
                  <h4>Total Documents</h4>
                  <p>1,200</p>
                </div>
              </div>

              <div className="stat-card gradient-green">
                <div className="icon-box">
                <FaClinicMedical />
                </div>
                <div className="stat-info">
                  <h4>Medical Care</h4>
                  <p>450</p>
                </div>
              </div>

              <div className="stat-card gradient-orange">
                <div className="icon-box">
                <FaPills />
                </div>
                <div className="stat-info">
                  <h4>Prescriptions</h4>
                  <p>320</p>
                </div>
              </div>

              <div className="stat-card gradient-purple">
                <div className="icon-box">
                <AiOutlineCalendar />
                </div>
                <div className="stat-info">
                  <h4>Scanned Today</h4>
                  <p>75</p>
                </div>
              </div>
    </div>
      <div className="charts-row">
        <div className="chart-box">
          <h4>Distribution of document types</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={documentTypeStats} cx="50%" cy="50%" outerRadius={100} label dataKey="value">
                {documentTypeStats.map((entry, index) => (<Cell key={index} fill={COLORS[index % COLORS.length]} />))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box">
          <h4>Designation type</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={donutData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} label dataKey="value">
                {donutData.map((entry, index) => (<Cell key={index} fill={COLORS[index % COLORS.length]} />))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );

  const renderPage2 = () => (
    <>
      <h2>Dashboard</h2>
      <div className="chart-box2">
        <h4>Scanned documents per month</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}><XAxis dataKey="name" />
          <YAxis /><Tooltip />
          <Bar dataKey="documents" fill="#0EA5E9" barSize={50}/></BarChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-box2">
        <h4>Monthly Reimbursements</h4>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={lineData}><XAxis dataKey="month" /><YAxis /><Tooltip /><CartesianGrid strokeDasharray="3 3" /><Line type="monotone" dataKey="remboursement" stroke="#14b8a6" /></LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );

  const renderPage3 = () => (
    <>
      <h2>Dashboard</h2>
      <div className="chart-box2">
        <h4>Users activities</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stackedData} stackOffset="sign">
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="scanned medical care" stackId="a" fill="#8884d8" />
            <Bar dataKey="scanned prescription" stackId="a" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );

  return (
    <div className="statistics">
      <div className="statistics-container">
        {page === 1 && renderPage1()}
        {page === 2 && renderPage2()}
        {page === 3 && renderPage3()}
        <div className="pagination">
          {[1, 2, 3].map((p) => (
            <button key={p} onClick={() => setPage(p)} className={page === p ? "active" : ""}>{p}</button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Statistics;
