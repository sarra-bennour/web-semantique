import React, { useState, useEffect } from 'react';
import { locationsAPI } from '../../utils/api';

const Locations = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [searchFilters, setSearchFilters] = useState({
    city: '',
    min_capacity: '',
    max_price: ''
  });

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await locationsAPI.getAll();
      setLocations(response.data);
    } catch (error) {
      console.error('Erreur chargement locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableLocations = async () => {
    try {
      const response = await locationsAPI.getAvailable();
      setLocations(response.data);
    } catch (error) {
      console.error('Erreur chargement locations disponibles:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await locationsAPI.search(searchFilters);
      setLocations(response.data);
    } catch (error) {
      console.error('Erreur recherche locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setSearchFilters({ city: '', min_capacity: '', max_price: '' });
    fetchLocations();
  };

  const toggleAvailableOnly = () => {
    if (!showAvailableOnly) {
      fetchAvailableLocations();
    } else {
      fetchLocations();
    }
    setShowAvailableOnly(!showAvailableOnly);
  };

  if (loading) return <div className="loading">Chargement des locations...</div>;

  return (
    <div className="locations-section">
      <h2>Locations d'Événements</h2>
      
      {/* Filtres et contrôles */}
      <div className="locations-controls">
        <button 
          onClick={toggleAvailableOnly} 
          className={`toggle-button ${showAvailableOnly ? 'active' : ''}`}
        >
          {showAvailableOnly ? 'Toutes les locations' : 'Locations disponibles seulement'}
        </button>
      </div>

      {/* Formulaire de recherche avancée */}
      <form onSubmit={handleSearch} className="search-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Ville..."
            value={searchFilters.city}
            onChange={(e) => handleFilterChange('city', e.target.value)}
            className="filter-input"
          />
          <input
            type="number"
            placeholder="Capacité minimum..."
            value={searchFilters.min_capacity}
            onChange={(e) => handleFilterChange('min_capacity', e.target.value)}
            className="filter-input"
          />
          <input
            type="number"
            placeholder="Prix maximum..."
            value={searchFilters.max_price}
            onChange={(e) => handleFilterChange('max_price', e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-buttons">
          <button type="submit" className="filter-button">Rechercher</button>
          <button type="button" onClick={clearFilters} className="filter-button clear">
            Effacer
          </button>
        </div>
      </form>

      {/* Liste des locations */}
      <div className="locations-grid">
        {locations.length > 0 ? (
          locations.map((location, index) => (
            <div key={index} className="location-card">
              <h3>{location.name}</h3>
              <div className="location-details">
                <p><strong>Adresse:</strong> {location.address}</p>
                {location.city && <p><strong>Ville:</strong> {location.city}</p>}
                {location.country && <p><strong>Pays:</strong> {location.country}</p>}
                <p><strong>Capacité:</strong> {location.capacity} personnes</p>
                <p><strong>Prix:</strong> {location.price || '0'} €</p>
                {location.description && (
                  <p className="location-description">{location.description}</p>
                )}
                <div className="location-status">
                  {location.reserved === 'true' && <span className="status reserved">Réservée</span>}
                  {location.inRepair === 'true' && <span className="status repair">En réparation</span>}
                  {(!location.reserved || location.reserved === 'false') && 
                   (!location.inRepair || location.inRepair === 'false') && 
                   <span className="status available">Disponible</span>}
                </div>
              </div>
            </div>
          ))
        ) : (
          <p>Aucune location trouvée</p>
        )}
      </div>
    </div>
  );
};

export default Locations;