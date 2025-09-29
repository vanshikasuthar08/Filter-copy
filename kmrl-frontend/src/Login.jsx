import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await axios.post('http://localhost:8004/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const accessToken = response.data.access_token;
      
      // --- NEW: Save the token to the browser's notepad ---
      localStorage.setItem('accessToken', accessToken);
      
      // --- NEW: Refresh the page to show the new view ---
      window.location.reload();
      
    } catch (err) {
      setError('Incorrect username or password. Please try again.');
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <img src="\kmrl-logo.png" alt="KMRL Logo" className="logo" />
          <h2>Document Hub Login</h2>
          <p>Kochi Metro Rail Limited</p>
        </div>
        <form onSubmit={handleSubmit}>
          {error && <p className="error-message">{error}</p>}
          <div className="input-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="login-button">Sign In</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
