import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Campaigns.css';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/campaigns');
    const uniqueCampaigns = removeDuplicates(response.data.results.bindings, 'name');
    setCampaigns(uniqueCampaigns);
    setLoading(false);
  } catch (error) {
    console.error('Erreur lors du chargement des campagnes:', error);
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

  if (loading) return <div className="loading">Chargement des campagnes...</div>;

  return (
    <div className="campaigns-page">
      <h1>Campagnes Écologiques</h1>
      <div className="campaigns-grid">
        {campaigns.map((campaign, index) => (
          <div key={index} className="campaign-card">
            <h3>{campaign.name?.value}</h3>
            <p>{campaign.description?.value || 'Pas de description'}</p>
            <div className="campaign-details">
              <span className={`status ${campaign.status?.value}`}>
                Statut: {campaign.status?.value || 'Inconnu'}
              </span>
              {campaign.startDate && (
                <span>Début: {new Date(campaign.startDate.value).toLocaleDateString()}</span>
              )}
              {campaign.endDate && (
                <span>Fin: {new Date(campaign.endDate.value).toLocaleDateString()}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Campaigns;