import React, { useState, useEffect } from 'react';
import { locationsAPI } from '../../utils/api';
import './style.css';

const Locations = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
 

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


  if (loading) return <div className="loading">Chargement des locations...</div>;

  return (
    <div className="locations-section">
      <h1>Lieux d'Événements</h1>
            

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