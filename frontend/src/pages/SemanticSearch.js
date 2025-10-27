import React, { useState } from 'react';
import { searchAPI } from '../utils/api';
import './SemanticSearch.css';

const SemanticSearch = () => {
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const categorizedSuggestions = {
    "Campagnes": [
      "Quelles sont les campagnes actives ?",
      "Montre-moi les campagnes de nettoyage",
      "Quelles campagnes de sensibilisation existent ?",
      "Quelles campagnes de financement sont disponibles ?",
      "Combien y a-t-il de campagnes par type ?",
      "Quel est le nombre total de campagnes ?",
      "Trier les campagnes par date de début"
    ],
    "Ressources": [
      "Quelles ressources humaines sont disponibles ?",
      "Montre-moi les ressources matérielles",
      "Quels équipements sont disponibles ?",
      "Quelles ressources financières avons-nous ?",
      "Quelles ressources numériques existent ?",
      "Combien y a-t-il de ressources par catégorie ?",
      "Quel est le nombre total de ressources ?",
      "Trier les ressources par coût"
    ],
    "Événements": [
      "Tous les événements",
      "Événements à venir",
      "Événements passés",
      "Événements éducatifs",
      "Événements compétitifs",
      "Événements de divertissement",
      "Événements de socialisation",
      "Qui organise les événements ?",
      "Montre-moi les organisateurs d'événements",
    ],
    "Blogs": [
      "Quels sont les derniers articles de blog ?",
      "Donne-moi les titres des blogs sur le compost",
      "Combien y a-t-il de blogs ?",
      "Liste des blogs par date",
      "Montre-moi les articles sur l'énergie solaire",
      "Quels blogs parlent de réduction des déchets ?"
    ],
    "Locations": [
      "Où se déroulent les événements ?",
      "Quels événements ont lieu à Paris ?",
      "Événements ont lieu à New York ",
      "Locations disponibles",
      "Locations à Boston",
    ],
    "Volontaires": [
    "Quels sont les volontaires ?",
    "Quels volontaires sont actifs ?",
    "Quelles sont les compétences des volontaires ?",
    "Quels volontaires ont de l'expérience ?",
    "Quels sont les contacts des volontaires ?"
    ],
    "assignements":
    [
        "Quels sont les assignements ?",
    "Quels assignements sont approuvés ?",
    "Quels assignements sont rejetés ?",
    "Quelles sont les notes des assignements ?",
    "Statistiques des assignements"
    ],
    "Certificats": [
      "Quelles certifications ont été émises ?",
      "Qui a reçu des certifications ?",
      "Quels types de certifications existent ?",
      "Montre-moi les certifications par points",
      "Qui émet les certifications ?"
    ],
    "Réservations": [
      "Quelles réservations sont confirmées ?",
      "Qui a fait des réservations ?",
      "Quelles réservations sont en attente ?",
      "Montre-moi les réservations par événement",
    ]
  };

  // Perform a semantic search for the given question text
  const performSemanticSearch = async (q) => {
    if (!q || !q.trim()) return;

    setQuestion(q);
    setLoading(true);
    try {
      const response = await searchAPI.semanticSearch(q);
      setResults(response.data);
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      setResults({ error: 'Erreur lors de la recherche sémantique' });
    }
    setLoading(false);
  };

  const handleSearch = (e) => {
    // form submit wrapper: prevent default and call performSemanticSearch
    if (e && e.preventDefault) e.preventDefault();
    performSemanticSearch(question);
  };

  const handleSuggestionClick = (suggestion) => {
    // When user clicks a suggested question, immediately run the semantic search
    performSemanticSearch(suggestion);
  };

  // Fonction pour afficher les résultats de comptage
  const renderCountResults = (resultsData) => {
    // Vérifier que resultsData est un tableau
    if (!Array.isArray(resultsData) || resultsData.length === 0) {
      return null;
    }

    // Résultat de comptage total campagnes
    if (resultsData.length === 1 && resultsData[0].hasOwnProperty('totalCampaigns')) {
      return (
        <div className="count-result">
          <h4>Nombre total de campagnes: {resultsData[0].totalCampaigns.value}</h4>
        </div>
      );
    }
    
    // Résultat de comptage total ressources
    if (resultsData.length === 1 && resultsData[0].hasOwnProperty('totalResources')) {
      return (
        <div className="count-result">
          <h4>Nombre total de ressources: {resultsData[0].totalResources.value}</h4>
        </div>
      );
    }
    
    // Résultat de comptage par type/catégorie
    if (resultsData.some(row => row.hasOwnProperty('count'))) {
      return (
        <div className="count-results">
          <h4>Répartition:</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Catégorie/Type</th>
                <th>Nombre</th>
              </tr>
            </thead>
            <tbody>
              {resultsData.map((row, index) => (
                <tr key={index}>
                  <td>
                    {row.type ? row.type.value : 
                     row.category ? row.category.value : 'Non catégorisé'}
                  </td>
                  <td>{row.count.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    
    return null;
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
                         Array.isArray(results.results) ? results.results : [];

    const questionText = results.question || results.original_question;
    const sparqlQuery = results.sparql_query || results.generated_sparql;

    // Vérifier d'abord si c'est un résultat de comptage
    const countResults = renderCountResults(resultsData);
    if (countResults) {
      return (
        <div className="results">
          <h3>Résultats pour: "{questionText}"</h3>
          {sparqlQuery && (
            <div className="sparql-query">
              <strong>Requête SPARQL générée:</strong>
              <pre>{sparqlQuery}</pre>
            </div>
          )}
          {countResults}
        </div>
      );
    }

    // Affichage normal des résultats
    return (
      <div className="results">
        <h3>Résultats pour: "{questionText}"</h3>
        
        {sparqlQuery && (
          <div className="sparql-query">
            <strong>Requête SPARQL générée:</strong>
            <pre>{sparqlQuery}</pre>
          </div>
        )}
        
        {hasBindings && Array.isArray(resultsData) && resultsData.length > 0 ? (
          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {/* Filter out internal id column 'b' and similar resource keys */}
                  {Object.keys(resultsData[0]).filter(key => !["b", "resource", "item"].includes(key)).map(key => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {resultsData.map((row, index) => (
                  <tr key={index}>
                    {Object.keys(row).filter(key => !["b", "resource", "item"].includes(key)).map((cellKey, cellIndex) => {
                      const cell = row[cellKey];
                      const value = cell && cell.value ? String(cell.value) : 'N/A';
                      return (
                        <td key={cellIndex}>
                          {value.length > 50 ? value.substring(0, 50) + '...' : value}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : hasArrayResults && Array.isArray(resultsData) && resultsData.length > 0 ? (
          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {Object.keys(resultsData[0]).filter(key => !["b", "resource", "item"].includes(key)).map(key => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {resultsData.map((row, index) => (
                  <tr key={index}>
                    {Object.keys(row).filter(key => !["b", "resource", "item"].includes(key)).map((k, cellIndex) => (
                      <td key={cellIndex}>
                        {String(row[k]).length > 50 
                          ? String(row[k]).substring(0, 50) + '...' 
                          : String(row[k])
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
      <p>Posez votre question en langage naturel sur les campagnes, ressources, événements, locations, utilisateurs, réservations et certifications</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Posez votre question en français... Ex: Quelles sont les campagnes actives ?"
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-button">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {/* Suggested Questions Section - Organisée par catégories */}
      <div className="suggestions">
        <h4>Questions suggérées par catégorie:</h4>
        
        {/* Campagnes */}
        <div className="suggestion-category">
          <h5>🏆 Campagnes</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Campagnes.map((suggestion, index) => (
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

        {/* Ressources */}
        <div className="suggestion-category">
          <h5>🛠️ Ressources</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Ressources.map((suggestion, index) => (
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

        {/* Les autres catégories restent inchangées */}
        <div className="suggestion-category">
          <h5>📅 Événements</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Événements.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>🏢 Locations</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Locations.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>👥 Volontaires</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Volontaires.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>📝 Blogs</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Blogs.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>📋 Assignements</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.assignements.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>📜 Certificats</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Certificats.map((suggestion, index) => (
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

        <div className="suggestion-category">
          <h5>📋 Réservations</h5>
          <div className="suggestion-buttons">
            {categorizedSuggestions.Réservations.map((suggestion, index) => (
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
      </div>

      {renderResults()}
    </div>
  );
};

export default SemanticSearch;