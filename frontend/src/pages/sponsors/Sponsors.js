import React, { useState, useEffect } from 'react';
import { sponsorsAPI, donationsAPI } from '../../utils/api';
import './Sponsors.css';

const Sponsors = () => {
  const [sponsors, setSponsors] = useState([]);
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ name: '', industry: '' });
  const [expandedSponsor, setExpandedSponsor] = useState(null);

  useEffect(() => {
    fetchSponsors();
    fetchDonations();
  }, []);

  const fetchSponsors = async () => {
    try {
      const res = await sponsorsAPI.getAll();
      setSponsors(res.data);
    } catch (err) {
      console.error('Erreur chargement sponsors:', err);
    }
  };

  const fetchDonations = async () => {
    try {
      const res = await donationsAPI.getAll();
      setDonations(res.data);
    } catch (err) {
      console.error('Erreur chargement donations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await sponsorsAPI.search(filters);
      setSponsors(res.data);
    } catch (err) {
      console.error('Erreur recherche sponsors:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  if (loading) return <div>Chargement des sponsors...</div>;

  return (
    <div className="sponsors-page">
      <h2>Sponsors et Donations</h2>

      <form onSubmit={handleSearch} className="sponsors-search">
        <input
          type="text"
          placeholder="Nom de l'entreprise..."
          value={filters.name}
          onChange={(e) => handleChange('name', e.target.value)}
        />
        <input
          type="text"
          placeholder="Secteur..."
          value={filters.industry}
          onChange={(e) => handleChange('industry', e.target.value)}
        />
        <button type="submit">Rechercher</button>
      </form>

      <div className="sponsors-list">
        <h3>Liste des sponsors</h3>
        {sponsors.length > 0 ? (
              <div className="events-grid">
            {sponsors.map((s, idx) => {
              const name = s.nomEntreprise || s.companyName || s.firstName || s.name || 'Sponsor';
              // find donations for this sponsor by matching donor name
              const donationsFor = donations.filter(d => {
                const donor = d.donateur || d.donorName || d.donor || '';
                return donor && donor === name;
              });
              return (
                <div key={idx} className="event-card">
                  <h4>{name}</h4>
                      <div className="event-details">
                        { (s.secteur || s.industry) && <p><strong>Secteur:</strong> {s.secteur || s.industry}</p> }
                        { (s.niveauDeSponsoring || s.levelName) && <p><strong>Niveau:</strong> {s.niveauDeSponsoring || s.levelName}</p> }
                        { (s.courriel || s.contactEmail || s.email) && <p><strong>Email:</strong> {s.courriel || s.contactEmail || s.email}</p> }
                        { (s.telephone || s.phoneNumber || s.phone) && <p><strong>Téléphone:</strong> {s.telephone || s.phoneNumber || s.phone}</p> }
                        { (s.siteWeb || s.website) && <p><strong>Site Web:</strong> <a href={(s.siteWeb || s.website).startsWith('http') ? (s.siteWeb || s.website) : `https://${s.siteWeb || s.website}`} target="_blank" rel="noreferrer">{s.siteWeb || s.website}</a></p> }
                      </div>

                  <div className="sponsor-actions">
                    <div className="sponsor-donations-count">Donations: {donationsFor.length}</div>
                    <button onClick={() => setExpandedSponsor(expandedSponsor === idx ? null : idx)}>{expandedSponsor === idx ? 'Masquer' : 'Voir donations'}</button>
                  </div>

                  {expandedSponsor === idx && (
                    <div className="sponsor-donations-list">
                      {donationsFor.length > 0 ? (
                        <ul>
                          {donationsFor.map((d, di) => (
                            <li key={di}>{d.rdfs_label || d.donation || d.label || d.rdfsLabel || 'Donation'} — {d.montant || d.amount || ''} {d.devise || d.currency || ''} </li>
                          ))}
                        </ul>
                      ) : (
                        <div>Aucune donation trouvée pour ce sponsor</div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <p>Aucun sponsor trouvé</p>
        )}
      </div>

      {/* Removed donations summary from sponsors page - donations are shown in the Donations page */}
    </div>
  );
};

export default Sponsors;
