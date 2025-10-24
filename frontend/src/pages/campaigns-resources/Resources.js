import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Resources.css';

const Resources = () => {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/resources');
    const uniqueResources = removeDuplicates(response.data.results.bindings, 'name');
    setResources(uniqueResources);
    setLoading(false);
  } catch (error) {
    console.error('Erreur lors du chargement des ressources:', error);
    setLoading(false);
  }
};

// Fonction utilitaire pour dédupliquer
const removeDuplicates = (array, key) => {
  const seen = new Set();
  return array.filter(item => {
    const value = item[key]?.value;
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
};
  if (loading) return <div className="loading">Chargement des ressources...</div>;

  return (
    <div className="resources-page">
      <h1>Ressources Écologiques</h1>
      <div className="resources-grid">
        {resources.map((resource, index) => (
          <div key={index} className="resource-card">
            <h3>{resource.name?.value}</h3>
            <p>{resource.description?.value || 'Pas de description'}</p>
            <div className="resource-details">
              <span>Catégorie: {resource.category?.value || 'Non spécifiée'}</span>
              {resource.quantity && (
                <span className="quantity">
                  Quantité: {resource.quantity.value}
                </span>
              )}
              {resource.unitCost && (
                <span className="unit-cost">
                  Coût unitaire: {resource.unitCost.value}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Resources;