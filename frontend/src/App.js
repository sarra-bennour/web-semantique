import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Campaigns from './pages/campaigns-resources/Campaigns';
import Resources from './pages/campaigns-resources/Resources';
import Users from './pages/Users';
import SemanticSearch from './pages/SemanticSearch';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Campaigns />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/users" element={<Users />} />
            <Route path="/search" element={<SemanticSearch />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;