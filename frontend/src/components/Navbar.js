import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="nav-container">
<a href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
  <h1 className="nav-logo">🌿 Eco Platform</h1>
</a>        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/campaigns" className="nav-link">Campagnes</Link>
          </li>
          <li className="nav-item">
            <Link to="/resources" className="nav-link">Ressources</Link>
          </li>

          <li className="nav-item">
            <Link to="/events" className="nav-link">Événements</Link>
          </li>
          <li className="nav-item">
            <Link to="/locations" className="nav-link">Locations</Link>
          </li>
          <li className="nav-item">
            <Link to="/reservations" className="nav-link">Réservations</Link>
          </li>
          <li className="nav-item">
            <Link to="/certifications" className="nav-link">Certifications</Link>
          </li>
          <li className="nav-item">
            <Link to="/volunteers" className="nav-link">Volontaires</Link>
          </li>
          <li className="nav-item">
            <Link to="/assignments" className="nav-link">Assignements</Link>
          </li>
          <li className="nav-item">
            <Link to="*" className="nav-link">Sponsors</Link>
          </li>
          <li className="nav-item">
            <Link to="*" className="nav-link">Donations</Link>
          </li>
          <li className="nav-item">
            <Link to="*" className="nav-link">Blogs</Link>
          </li>

          <li className="nav-item">
            <Link to="/users" className="nav-link">Utilisateurs</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;