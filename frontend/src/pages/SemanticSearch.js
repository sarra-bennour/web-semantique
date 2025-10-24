import React, { useState } from 'react';
import axios from 'axios';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/search/semantic', {
        question: question
      });
      setResults(response.data);
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      alert('Erreur lors de la recherche sémantique');
    }
    setLoading(false);
  };

  return (
    <div className="semantic-search">
      <h1>Recherche Sémantique</h1>
      <p>Posez votre question en langage naturel sur les campagnes, ressources et utilisateurs</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ex: Quelles sont les campagnes actives ?"
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-button">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {results && (
        <div className="results">
          <h3>Résultats pour: "{results.original_question}"</h3>
          
          {/* <div className="sparql-query">
            <h4>Requête SPARQL générée:</h4>
            <pre>{results.generated_sparql}</pre>
          </div> */}

          <div className="search-results">
            <h4>Résultats:</h4>
            {results.results.results.bindings.length > 0 ? (
              <table className="results-table">
                <thead>
                  <tr>
                    {Object.keys(results.results.results.bindings[0]).map(key => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.results.results.bindings.map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((cell, cellIndex) => (
                        <td key={cellIndex}>{cell.value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>Aucun résultat trouvé</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SemanticSearch;