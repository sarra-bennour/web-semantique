from flask import Blueprint, jsonify
from sparql_utils import sparql_utils

volunteers_bp = Blueprint('volunteers', __name__)

@volunteers_bp.route('/volunteers', methods=['GET'])
def get_all_volunteers():
    """Récupère tous les volontaires"""
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
    }
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/<volunteer_id>', methods=['GET'])
def get_volunteer(volunteer_id):
    """Récupère un volontaire spécifique"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {{
        <{volunteer_id}> a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL {{ <{volunteer_id}> rdfs:label ?label . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }}
        OPTIONAL {{ <{volunteer_id}> <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }}
    }}
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results[0] if results else {})

@volunteers_bp.route('/volunteers/search', methods=['POST'])
def search_volunteers():
    """Recherche de volontaires par critères"""
    from flask import request
    
    data = request.json
    skills = data.get('skills', '')
    activity_level = data.get('activity_level', '')
    medical_conditions = data.get('medical_conditions', '')
    
    query = """
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?medicalConditions ?motivation ?experience ?skills ?activityLevel ?generalMotivation
    WHERE {
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
        
        OPTIONAL { ?volunteer rdfs:label ?label . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
        OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
    """
    
    filters = []
    if skills:
        filters.append(f'REGEX(?skills, "{skills}", "i")')
    if activity_level:
        filters.append(f'REGEX(?activityLevel, "{activity_level}", "i")')
    if medical_conditions:
        filters.append(f'REGEX(?medicalConditions, "{medical_conditions}", "i")')
    
    if filters:
        query += " FILTER(" + " && ".join(filters) + ")"
    
    query += "} ORDER BY ?label"
    
    results = sparql_utils.execute_query(query)
    return jsonify(results)

@volunteers_bp.route('/volunteers/by-activity-level/<level>', methods=['GET'])
def get_volunteers_by_activity_level(level):
    """Récupère les volontaires par niveau d'activité"""
    query = f"""
    PREFIX webprotege: <http://webprotege.stanford.edu/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?volunteer ?label ?user ?phone ?skills ?activityLevel
    WHERE {{
        ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> ;
                  <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
        
        OPTIONAL {{ ?volunteer rdfs:label ?label . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
        OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }}
        
        FILTER(REGEX(?activityLevel, "{level}", "i"))
    }}
    ORDER BY ?label
    """
    results = sparql_utils.execute_query(query)
    return jsonify(results)
