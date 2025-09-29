import React from 'react';
import './LandingPage.css';

function LandingPage() {
  const handleLoginClick = () => {
    // When any department card is clicked, we go to the login page
    window.location.hash = '#login';
  };

  return (
    <div className="landing-container">
      <header className="landing-header">
        <img src="/kmrl-logo.png" alt="KMRL Logo" className="header-logo" />
        <nav>
          <span>WHO WE ARE</span>
          <span>WHAT WE DO</span>
          <span>ENVIRONMENT & SOCIAL</span>
          <span>PASSENGER INFO</span>
          <span>VIGILANCE</span>
        </nav>
      </header>
      
      <div className="hero-section">
        <a href="#login" className="hero-text-link">
          <div className="hero-text">
            <h1>ADMIN LOGIN</h1>
            <p>Home / About Us</p>
          </div>
        </a>
      </div>

      <section className="departments-section">
        <h2>OUR DEPARTMENTS</h2>
        <div className="departments-grid">
          <div className="department-card" onClick={handleLoginClick}>
            <img src="Engineering.jpg" alt="Engineering" />
            <div className="card-title">ENGINEERING DEPARTMENT</div>
          </div>
          <div className="department-card" onClick={handleLoginClick}>
            <img src="Contract.jpg" alt="Contract" />
            <div className="card-title">CONTRACT DEPARTMENT</div>
          </div>
          <div className="department-card" onClick={handleLoginClick}>
            <img src="Legal.jpg" alt="Legal" />
            <div className="card-title">LEGAL DEPARTMENT</div>
          </div>
          <div className="department-card" onClick={handleLoginClick}>
            <img src="Complaint.jpg" alt="Complaint" />
            <div className="card-title">COMPLAINT DEPARTMENT</div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
