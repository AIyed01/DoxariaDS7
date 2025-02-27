import logo from './logo.svg';
import './App.css';
import Home from './components/Home';
import FaceRecognition from './components/FaceRecognitioin';
import { Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const isLoggedInStr = localStorage.getItem('isLoggedIn');
    if (isLoggedInStr === 'true') {
      setIsLoggedIn(true);
    }
  },[])
  const handleLogin = (loggedIn) => {
    setIsLoggedIn(loggedIn);
    localStorage.setItem('isLoggedIn', loggedIn);
  };
  const handleLogout =()=>{
    setIsLoggedIn(false);
    localStorage.setItem('isLoggedIn', false);
  }
  return (
    <Routes>
      <Route path="/" element={isLoggedIn===true ? <Home handleLogout={handleLogout}/> : <FaceRecognition handleLogin={handleLogin}/> }/>
      <Route path={!isLoggedIn ? "/login" : "/"} element={<FaceRecognition handleLogin={handleLogin}/>} />
    </Routes>
  );
}

export default App;
