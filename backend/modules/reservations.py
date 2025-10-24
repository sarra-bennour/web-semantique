from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations', methods=['GET'])
def get_reservations():
    """Récupère toutes les réservations"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail ?confirmedByName ?confirmedByEmail
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }
            OPTIONAL { ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }
            OPTIONAL { 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }
            OPTIONAL { 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL { ?user eco:email ?userEmail . }
            }
            OPTIONAL { 
                ?reservation eco:confirmedBy ?admin .
                ?admin eco:firstName ?confirmedByName .
                OPTIONAL { ?admin eco:email ?confirmedByEmail . }
            }
        }
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/status/<status>', methods=['GET'])
def get_reservations_by_status(status):
    """Récupère les réservations par statut (pending, confirmed, cancelled)"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
            FILTER(LCASE(STR(?status)) = "{status.lower()}")
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }}
            OPTIONAL {{ 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL {{ ?user eco:email ?userEmail . }}
            }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/event/<event_name>', methods=['GET'])
def get_reservations_by_event(event_name):
    """Récupère les réservations pour un événement spécifique"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
            ?event eco:eventTitle ?eventTitle .
            FILTER(CONTAINS(LCASE(STR(?eventTitle)), "{event_name.lower()}"))
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }}
            OPTIONAL {{ 
                ?reservation eco:belongsToUser ?user .
                ?user eco:firstName ?userName .
                OPTIONAL {{ ?user eco:email ?userEmail . }}
            }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/user/<user_name>', methods=['GET'])
def get_reservations_by_user(user_name):
    """Récupère les réservations d'un utilisateur spécifique"""
    try:
        query = f"""
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
        WHERE {{
            ?reservation a eco:Reservation .
            ?reservation eco:belongsToUser ?user .
            ?user eco:firstName ?userName .
            FILTER(CONTAINS(LCASE(STR(?userName)), "{user_name.lower()}"))
            OPTIONAL {{ ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }}
            OPTIONAL {{ ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }}
            OPTIONAL {{ 
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
            }}
            OPTIONAL {{ ?user eco:email ?userEmail . }}
        }}
        ORDER BY ?reservation
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservations_bp.route('/reservations/stats', methods=['GET'])
def get_reservations_stats():
    """Récupère les statistiques des réservations"""
    try:
        query = """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT ?status (COUNT(?reservation) as ?count)
        WHERE {
            ?reservation a eco:Reservation .
            OPTIONAL { ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status . }
        }
        GROUP BY ?status
        ORDER BY ?status
        """
        
        results = sparql_utils.execute_query(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
