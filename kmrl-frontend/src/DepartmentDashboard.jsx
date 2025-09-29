import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState({ role: 'Guest' });
  const [files, setFiles] = useState([]);
  const [currentFolder, setCurrentFolder] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const decodedToken = jwtDecode(token);
      setUser(decodedToken);
    }
  }, []);

  const handleFolderClick = async (folderType) => {
    setFiles([]); // Clear previous file list
    setCurrentFolder(folderType);
    setError('');
    try {
      const token = localStorage.getItem('accessToken');
      // Fetch files for the user's department and the clicked folder type
      const response = await axios.get(`http://localhost:8004/files/${user.role}/${folderType}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setFiles(response.data);
    } catch (err) {
      setError(`Could not fetch files from ${folderType} folder.`);
      console.error('Failed to fetch files:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    window.location.reload();
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-left">
          <img src="/kmrl-logo.png" alt="KMRL Logo" className="header-logo-small" />
          <h1>KMRL Document Hub</h1>
        </div>
        <div className="header-right">
          <span>Welcome, {user.role.charAt(0).toUpperCase() + user.role.slice(1)} Department</span>
          <button onClick={handleLogout} className="logout-button">Log Out</button>
        </div>
      </header>
      <main className="dashboard-main">
        <h2>{user.role.toUpperCase()} DEPARTMENT FOLDERS</h2>
        <div className="folder-grid">
          <div className="folder" onClick={() => handleFolderClick('Original')}>
            <span className="folder-icon">📁</span>
            <span className="folder-name">Original Files</span>
          </div>
          <div className="folder" onClick={() => handleFolderClick('Converted')}>
            <span className="folder-icon">📄</span>
            <span className="folder-name">Converted Files</span>
          </div>
          <div className="folder" onClick={() => handleFolderClick('NonConverted')}>
            <span className="folder-icon">❓</span>
            <span className="folder-name">Non-Converted Files</span>
          </div>
        </div>

        {currentFolder && (
          <div className="file-list">
            <h3>Files in: {currentFolder}</h3>
            {error && <p className="error-message">{error}</p>}
            <ul>
              {files.length > 0 ? (
                files.map((file, index) => (
                  <li key={index}>
                    <a href={file.url} target="_blank" rel="noopener noreferrer">
                      {file.name}
                    </a>
                    <span>({(file.size / 1024).toFixed(2)} KB)</span>
                  </li>
                ))
              ) : (
                <li>No files found in this folder.</li>
              )}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
