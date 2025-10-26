import React, { useState, useEffect } from 'react';
import { eventsAPI, locationsAPI } from '../../utils/api'; 
import '../events-locations/style.css';

const Events = () => {
  const [events, setEvents] = useState([]);
  const [locations, setLocations] = useState([]); // State for locations
  const [loading, setLoading] = useState(true);
  const [locationsLoading, setLocationsLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    title: '',
    location: '',
    date: ''
  });

  useEffect(() => {
    fetchEvents();
    fetchLocations();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await eventsAPI.getAll();
      console.log('API Response:', response);
      console.log('Events data:', response.data);
      setEvents(response.data);
    } catch (error) {
      console.error('Erreur chargement événements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await locationsAPI.getAll(); // Assuming you have this endpoint
      console.log('Locations data:', response.data);
      setLocations(response.data);
    } catch (error) {
      console.error('Erreur chargement des lieux:', error);
    } finally {
      setLocationsLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await eventsAPI.search(searchFilters);
      setEvents(response.data);
    } catch (error) {
      console.error('Erreur recherche événements:', error);
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
    setSearchFilters({ title: '', location: '', date: '' });
    fetchEvents();
  };

  const getImageArray = (imagesString) => {
    console.log('Images string:', imagesString);
    if (!imagesString || imagesString === 'undefined' || imagesString === 'null') return [];
    if (Array.isArray(imagesString)) return imagesString;
    
    const cleaned = imagesString.toString().trim();
    if (!cleaned) return [];
    
    return cleaned.split(',').map(img => {
      const trimmed = img.trim();
      if (trimmed.startsWith('http')) {
        return trimmed;
      }
      return `https://images.unsplash.com/${trimmed}`;
    }).filter(img => img !== '');
  };

  if (loading) return <div className="loading">Chargement des événements...</div>;

  return (
    <div className="events-section">
      <h1>Événements Écologiques</h1>
      
      {/* Formulaire de recherche */}
      <form onSubmit={handleSearch} className="search-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Rechercher par titre..."
            value={searchFilters.title}
            onChange={(e) => handleFilterChange('title', e.target.value)}
            className="filter-input"
          />
          
          {/* Dropdown for locations */}
          <select
            value={searchFilters.location}
            onChange={(e) => handleFilterChange('location', e.target.value)}
            className="filter-input"
          >
            <option value="">Tous les lieux</option>
            {locations.map((location, index) => (
              <option key={index} value={location.name || location.locationName}>
                {location.name || location.locationName}
              </option>
            ))}
          </select>
          
          <input
            type="date"
            placeholder="Date..."
            value={searchFilters.date}
            onChange={(e) => handleFilterChange('date', e.target.value)}
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

      {/* Liste des événements */}
      <div className="events-grid">
        {events.length > 0 ? (
          events.map((event, index) => {
            const eventImages = getImageArray(event.images);
            console.log(`Event ${index} images:`, eventImages);
            
            return (
              <div key={index} className="event-card">
                <div className="event-image-container">
                  {eventImages.length > 0 ? (
                    <img 
                      src={eventImages[0]} 
                      alt={event.title}
                      className="event-image"
                      onError={(e) => {
                        console.error(`Image failed to load: ${eventImages[0]}`);
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                  ) : null}
                  <div className="event-image-placeholder" style={{ 
                    display: eventImages.length > 0 ? 'none' : 'block' 
                  }}>
                    📷 Aucune image
                  </div>
                </div>
                
                <h3>{event.title}</h3>
                {event.description && (
                  <p className="event-description">{event.description}</p>
                )}
                <div className="event-details">
                  <p><strong>Date:</strong> {new Date(event.date).toLocaleString('fr-FR')}</p>
                  <p><strong>Lieu:</strong> {event.locationName || 'Non spécifié'}</p>
                  <p><strong>Participants max:</strong> {event.maxParticipants}</p>
                  {event.status && <p><strong>Statut:</strong> {event.status}</p>}
                  {event.duration && <p><strong>Durée:</strong> {event.duration}</p>}
                </div>
              </div>
            );
          })
        ) : (
          <p>Aucun événement trouvé</p>
        )}
      </div>
    </div>
  );
};

export default Events;