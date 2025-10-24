from flask import Flask, jsonify, request
from flask_cors import CORS
from modules.campRes import api_routes
import os
from modules.events import events_bp
from modules.locations import locations_bp
from modules.users import users_bp
from modules.search import search_bp
from modules.reservations import reservations_bp
from modules.certifications import certifications_bp
from sparql_utils import sparql_utils

app = Flask(__name__)
CORS(app)

# Enregistrement des routes
app.register_blueprint(api_routes, url_prefix='/api')
app.register_blueprint(events_bp, url_prefix='/api')
app.register_blueprint(locations_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(reservations_bp, url_prefix='/api')
app.register_blueprint(certifications_bp, url_prefix='/api')


@app.route('/')
def home():
    return jsonify({"message": "Eco Platform API is running!"})



@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de santé de l'API"""
    return jsonify({"status": "OK", "message": "API fonctionnelle"})


@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test de connexion à Fuseki et aux données"""
    try:
        if not sparql_utils:
            return jsonify({
                "status": "error",
                "message": "SPARQL utils non initialisé"
            }), 500
            
        # Test simple de comptage
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        results = sparql_utils.execute_query(query)
        
        # Test des événements
        events_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?event_count) WHERE {
            ?event a eco:Event .
        }
        """
        events_results = sparql_utils.execute_query(events_query)
        
        # Test des locations
        locations_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?location_count) WHERE {
            ?location a eco:Location .
        }
        """
        locations_results = sparql_utils.execute_query(locations_query)
        
        # Test des utilisateurs
        users_query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT (COUNT(*) as ?user_count) WHERE {
            ?user a eco:User .
        }
        """
        users_results = sparql_utils.execute_query(users_query)
        
        return jsonify({
            "status": "success",
            "message": "Connexion Fuseki OK",
            "data_summary": {
                "total_triplets": results[0].get('count', 0) if results else 0,
                "total_events": events_results[0].get('event_count', 0) if events_results else 0,
                "total_locations": locations_results[0].get('location_count', 0) if locations_results else 0,
                "total_users": users_results[0].get('user_count', 0) if users_results else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur test Fuseki: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur Fuseki: {str(e)}"
        }), 500
    


if __name__ == '__main__':
    app.run(debug=True, port=5000)