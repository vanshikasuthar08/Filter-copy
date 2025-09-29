import React, { useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import Login from './Login';
import DepartmentDashboard from './DepartmentDashboard'; // Renamed for clarity
import AdminDashboard from './AdminDashboard'; // Import the new admin dash
import LandingPage from './LandingPage';

function App() {
  const [route, setRoute] = useState(window.location.hash);
  const [user, setUser] = useState(null);

  // Check for a token on initial load and when the app starts
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const decodedToken = jwtDecode(token);
      setUser(decodedToken);
    }
  }, []);

  // Listen for URL changes to show the login page
  useEffect(() => {
    const handleHashChange = () => setRoute(window.location.hash);
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // --- The Main Routing Logic ---
  if (user) { // If a user is logged in
    if (user.role === 'admin') {
      return <AdminDashboard />; // Show admin dashboard
    } else {
      return <DepartmentDashboard />; // Show department dashboard
    }
  } else { // If no user is logged in
    if (route === '#login') {
      return <Login />; // Show login page if URL has #login
    } else {
      return <LandingPage />; // Default to the landing page
    }
  }
}

export default App;



