import React, { useState, useEffect } from 'react';
import { donationsAPI } from '../../utils/api';
import './Donations.css';

const Donations = () => {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDonations();
  }, []);

  const fetchDonations = async () => {
    try {
      const res = await donationsAPI.getAll();
      setDonations(res.data || []);
    } catch (err) {
      console.error('Erreur chargement donations:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Chargement des donations...</div>;

  return (
    <div className="donations-page">
      <h2>Donations</h2>
      {donations.length > 0 ? (
        <div className="reservations-grid">
          {donations.map((d, idx) => (
            <div key={idx} className="reservation-card">
              <div className="reservation-header">
                <h3>{d.rdfs_label || d.rdfsLabel || d.label || d.donation || `Donation ${idx + 1}`}</h3>
                <div className="results-count">{d.montant || d.amount ? `${d.montant || d.amount} ${d.devise || d.currency || ''}` : ''}</div>
              </div>
              <div className="reservation-details">
                <div className="detail-row"><div className="detail-label">Donateur</div><div className="detail-value">{d.donateur || d.donorName || ''}</div></div>
                <div className="detail-row"><div className="detail-label">Détails</div><div className="detail-value">{d.description || d.itemDescription || d.serviceDescription || ''}</div></div>
                <div className="detail-row"><div className="detail-label">Valeur estimée</div><div className="detail-value">{d.valeurEstimee || d.estimatedValue || ''}</div></div>
                <div className="detail-row"><div className="detail-label">Heures</div><div className="detail-value">{d.heuresDonnees || d.hoursDonated || ''}</div></div>
                <div className="detail-row"><div className="detail-label">Événement</div><div className="detail-value">{d.evenement || d.eventTitle || ''}</div></div>
                <div className="detail-row"><div className="detail-label">Date</div><div className="detail-value">{d.date ? new Date(d.date).toLocaleString('fr-FR') : ''}</div></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="donations-empty">Aucune donation trouvée</p>
      )}
    </div>
  );
};

export default Donations;
