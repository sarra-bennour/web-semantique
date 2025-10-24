import React, { useState, useEffect } from 'react';
import { usersAPI } from '../utils/api';
import './Users.css';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getAll();
      setUsers(response.data);
    } catch (error) {
      console.error('Erreur chargement utilisateurs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrganizers = async () => {
    try {
      const response = await usersAPI.getOrganizers();
      setUsers(response.data);
    } catch (error) {
      console.error('Erreur chargement organisateurs:', error);
    }
  };

  const fetchUsersByRole = async (role) => {
    try {
      const response = await usersAPI.getByRole(role);
      setUsers(response.data);
    } catch (error) {
      console.error(`Erreur chargement ${role}s:`, error);
    }
  };

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
    setLoading(true);

    switch (filter) {
      case 'all':
        fetchUsers();
        break;
      case 'organizers':
        fetchOrganizers();
        break;
      case 'volunteers':
        fetchUsersByRole('volunteer');
        break;
      default:
        fetchUsers();
    }
  };

  if (loading) return <div className="loading">Chargement des utilisateurs...</div>;

return (
  <div className="users-page">
    <h1>Utilisateurs</h1>
    
    {/* Filtres */}
    <div className="users-filters">
      <button 
        className={`filter-button ${activeFilter === 'all' ? 'active' : ''}`}
        onClick={() => handleFilterChange('all')}
      >
        Tous les utilisateurs
      </button>
      <button 
        className={`filter-button ${activeFilter === 'organizers' ? 'active' : ''}`}
        onClick={() => handleFilterChange('organizers')}
      >
        Organisateurs
      </button>
      <button 
        className={`filter-button ${activeFilter === 'volunteers' ? 'active' : ''}`}
        onClick={() => handleFilterChange('volunteers')}
      >
        Volontaires
      </button>
    </div>

    {/* Tableau des utilisateurs */}
    <table className="users-table">
      <thead>
        <tr>
          <th>Prénom</th>
          <th>Nom</th>
          <th>Email</th>
          <th>Rôle</th>
          <th>Date d'inscription</th>
        </tr>
      </thead>
      <tbody>
        {users.length > 0 ? (
          users.map((user, index) => (
            <tr key={index}>
              <td>{user.firstName?.value || user.firstName}</td>
              <td>{user.lastName?.value || user.lastName || '-'}</td>
              <td>{user.email?.value || user.email || '-'}</td>
              <td>
                <span className={`role-badge ${(user.role?.value || user.role)?.toLowerCase() || 'unknown'}`}>
                  {user.role?.value || user.role || 'Non spécifié'}
                </span>
              </td>
              <td>
                {(user.registrationDate?.value || user.registrationDate) 
                  ? new Date(user.registrationDate?.value || user.registrationDate).toLocaleDateString()
                  : '-'
                }
              </td>
            </tr>
          ))
        ) : (
          <tr>
            <td colSpan="5" style={{textAlign: 'center'}}>
              Aucun utilisateur trouvé
            </td>
          </tr>
        )}
      </tbody>
    </table>
  </div>
);
};

export default Users;