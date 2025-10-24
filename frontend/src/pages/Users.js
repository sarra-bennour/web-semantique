import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Users.css';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/users');
      setUsers(response.data.results.bindings);
      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Chargement des utilisateurs...</div>;

  return (
    <div className="users-page">
      <h1>Utilisateurs</h1>
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
          {users.map((user, index) => (
            <tr key={index}>
              <td>{user.firstName?.value}</td>
              <td>{user.lastName?.value || '-'}</td>
              <td>{user.email?.value || '-'}</td>
              <td>
                <span className={`role-badge ${user.role?.value?.toLowerCase() || 'unknown'}`}>
                  {user.role?.value || 'Non spécifié'}
                </span>
              </td>
              <td>
                {user.registrationDate?.value 
                  ? new Date(user.registrationDate.value).toLocaleDateString()
                  : '-'
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Users;