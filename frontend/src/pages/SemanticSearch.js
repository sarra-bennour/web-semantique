import React, { useState } from 'react';
import { searchAPI } from '../utils/api';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    "Quels sont les événements disponibles ?",
    "Où se déroulent les événements ?",
    "Qui organise les événements ?",
    "Qui sont les sponsors ?",
    "Quelles entreprises ont fait des donations ?",
    "Quelles locations sont disponibles ?",
    "Montre-moi les organisateurs d'événements",
    "Quels sont les volontaires ?",
    "Quels événements ont lieu à Paris ?",
    "Montre les donations pour un événement spécifique",
    "Quelles sont les campagnes actives ?",
    "Quelles ressources sont disponibles ?",
    "Quelles réservations sont confirmées ?",
    "Qui a fait des réservations ?",
    "Quelles réservations sont en attente ?",
    "Montre-moi les réservations par événement",
    "Quelles certifications ont été émises ?",
    "Qui a reçu des certifications ?",
    "Quels types de certifications existent ?",
    "Montre-moi les certifications par points",
    "Qui émet les certifications ?"
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      // CORRECTED: Use the searchAPI properly
      const response = await searchAPI.semanticSearch(question);
      setResults(response.data);
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      setResults({ error: 'Erreur lors de la recherche sémantique' });
    }
    setLoading(false);
  };

  const handleSuggestionClick = (suggestion) => {
    // Set the suggestion and run the search immediately
    setQuestion(suggestion);
    (async () => {
      setLoading(true);
      try {
        const response = await searchAPI.semanticSearch(suggestion);
        setResults(response.data);
      } catch (error) {
        console.error('Erreur lors de la recherche:', error);
        setResults({ error: 'Erreur lors de la recherche sémantique' });
      }
      setLoading(false);
    })();
  };

  const renderResults = () => {
    if (!results) return null;
    
    if (results.error) {
      return <div className="error">Erreur: {results.error}</div>;
    }

    // Handle both response formats
    const hasBindings = results.results && results.results.results && results.results.results.bindings;
    const hasArrayResults = results.results && Array.isArray(results.results);
    const hasDirectResults = Array.isArray(results.results);
    
    const resultsData = hasBindings ? results.results.results.bindings : 
                         hasArrayResults ? results.results :
                         hasDirectResults ? results.results : 
                         results.results || [];

    const questionText = results.question || results.original_question;
    const sparqlQuery = results.sparql_query || results.generated_sparql;

    return (
      <div className="results">
        <h3>Résultats pour: "{questionText}"</h3>
        
        {sparqlQuery && (
          <div className="sparql-query">
            <strong>Requête SPARQL générée:</strong>
            <pre>{sparqlQuery}</pre>
          </div>
        )}
        
        {hasBindings && resultsData.length > 0 ? (
          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {/* Build a stable header order: collect all keys across rows then use that as column order */}
                  {(() => {
                    const headerSet = new Set();
                    resultsData.forEach(row => Object.keys(row).forEach(k => headerSet.add(k)));
                    const headers = Array.from(headerSet);
                    return headers.map(key => (<th key={key}>{key}</th>));
                  })()}
                </tr>
              </thead>
              <tbody>
                {(() => {
                  const headerSet = new Set();
                  resultsData.forEach(row => Object.keys(row).forEach(k => headerSet.add(k)));
                  const headers = Array.from(headerSet);
                  return resultsData.map((row, index) => (
                    <tr key={index}>
                      {headers.map((h, cellIndex) => {
                        const cell = row[h];
                        const val = cell && cell.value ? String(cell.value) : '';
                        return (
                          <td key={cellIndex}>
                            {val ? (val.length > 50 ? val.substring(0, 50) + '...' : val) : 'N/A'}
                          </td>
                        );
                      })}
                    </tr>
                  ));
                })()}
              </tbody>
            </table>
          </div>
        ) : hasArrayResults && resultsData.length > 0 ? (
          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {Object.keys(resultsData[0]).map(key => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {resultsData.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, cellIndex) => (
                      <td key={cellIndex}>
                        {String(value).length > 50 
                          ? String(value).substring(0, 50) + '...' 
                          : String(value)
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>Aucun résultat trouvé</p>
        )}
      </div>
    );
  };

  return (
    <div className="semantic-search">
      <h1>Recherche Sémantique</h1>
      <p>Posez votre question en langage naturel sur les événements, locations, utilisateurs, campagnes, réservations, certifications, sponsors et donations</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Posez votre question en français... Ex: Quels sont les événements à Paris ?"
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-button">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {/* Suggested Questions Section */}
      <div className="suggestions">
        <h4>Questions suggérées:</h4>
        <div className="suggestion-buttons">
          {suggestedQuestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="suggestion-button"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {renderResults()}
    </div>
  );
};

export default SemanticSearch;