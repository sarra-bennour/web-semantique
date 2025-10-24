import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="nav-logo">🌿 Eco Platform</h1>
        <ul className="nav-menu">
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
            <Link to="/users" className="nav-link">Utilisateurs</Link>
          </li>
          <li className="nav-item">
            <Link to="/search" className="nav-link">Recherche Sémantique</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;