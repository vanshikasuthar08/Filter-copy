import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css'; // We'll reuse the same CSS

function AdminDashboard() {
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState(null);
  const [files, setFiles] = useState([]);
  const [currentFolder, setCurrentFolder] = useState('');
  const [error, setError] = useState('');

  // 1. Fetch the list of all departments when the page loads
  useEffect(() => {
    const fetchDepartments = async () => {
      const token = localStorage.getItem('accessToken');
      try {
        const response = await axios.get('http://localhost:8004/departments', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setDepartments(response.data);
      } catch (err) {
        setError('Could not fetch department list.');
      }
    };
    fetchDepartments();
  }, []);

  // 2. Function to fetch files for a selected department and folder
  const handleFolderClick = async (department, folderType) => {
    setFiles([]);
    setSelectedDept(department);
    setCurrentFolder(folderType);
    setError('');
    const token = localStorage.getItem('accessToken');
    try {
      const response = await axios.get(`http://localhost:8004/files/${department}/${folderType}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setFiles(response.data);
    } catch (err) {
      setError(`Could not fetch files for ${department}.`);
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
          <h1>KMRL Document Hub (Admin View)</h1>
        </div>
        <div className="header-right">
          <span>Welcome, Admin</span>
          <button onClick={handleLogout} className="logout-button">Log Out</button>
        </div>
      </header>
      <main className="dashboard-main">
        <h2>All Department Documents</h2>
        {error && <p className="error-message">{error}</p>}

        {/* List of Departments */}
        <div className="department-selector">
          {departments.map(dept => (
            <div key={dept} className={`department-tab ${selectedDept === dept ? 'active' : ''}`}>
              <h3>{dept.toUpperCase()}</h3>
              <div className="folder-grid-admin">
                <button onClick={() => handleFolderClick(dept, 'Original')}>Original</button>
                <button onClick={() => handleFolderClick(dept, 'Converted')}>Converted</button>
                <button onClick={() => handleFolderClick(dept, 'NonConverted')}>Non-Converted</button>
              </div>
            </div>
          ))}
        </div>

        {/* File List for the selected department/folder */}
        {currentFolder && (
          <div className="file-list">
            <h3>Files in: {selectedDept} / {currentFolder}</h3>
            <ul>
              {files.length > 0 ? (
                files.map((file, index) => (
                  <li key={index}>
                    <a href={file.url} target="_blank" rel="noopener noreferrer">{file.name}</a>
                    <span>({(file.size / 1024).toFixed(2)} KB)</span>
                  </li>
                ))
              ) : (
                <li>No files found.</li>
              )}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
}

export default AdminDashboard;

