from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
import re
from datetime import datetime, timedelta

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def semantic_search():
    """Recherche sémantique - transformation question en SPARQL"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').lower()
        
        # Transformation des questions en requêtes SPARQL
        sparql_query = transform_question_to_sparql_combined(question)
        
        if not sparql_query:
            return jsonify({"error": "Question non reconnue"}), 400
        
        # Exécution de la requête
        results = sparql_utils.execute_query(sparql_query)
        
        return jsonify({
            "question": question,
            "sparql_query": sparql_query,
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_city_from_question(question_lower):
    """Extract city name from question - SIMPLIFIED VERSION"""
    # List of known cities from your RDF
    known_cities = ['paris', 'london', 'new york', 'boston', 'chicago', 'san francisco', 'tunis']
    
    # Check for city patterns
    patterns = [
        r'à (\w+(?:\s+\w+)*)',
        r'in (\w+(?:\s+\w+)*)',
        r'ville de (\w+(?:\s+\w+)*)',
        r'city of (\w+(?:\s+\w+)*)',
        r'au (\w+(?:\s+\w+)*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question_lower)
        if match:
            potential_city = match.group(1).strip().lower()
            if potential_city in known_cities:
                return potential_city
    
    # Direct city mention
    for city in known_cities:
        if city in question_lower:
            return city
    
    return None

def extract_date_from_question(question_lower):
    """Extract date information from question"""
    # Today
    if any(word in question_lower for word in ['aujourd\'hui', 'today', 'ce jour']):
        return 'today'
    
    # Tomorrow
    elif any(word in question_lower for word in ['demain', 'tomorrow']):
        return 'tomorrow'
    
    # This week
    elif any(word in question_lower for word in ['cette semaine', 'this week', 'semaine actuelle']):
        return 'this_week'
    
    # This weekend
    elif any(word in question_lower for word in ['weekend', 'week-end', 'fin de semaine']):
        return 'weekend'
    
    # This month
    elif any(word in question_lower for word in ['ce mois', 'this month', 'mois actuel']):
        return 'this_month'
    
    # Future events
    elif any(word in question_lower for word in ['à venir', 'futur', 'future', 'upcoming', 'prochain']):
        return 'future'
    
    # Past events
    elif any(word in question_lower for word in ['passé', 'past', 'ancien', 'previous', 'terminé']):
        return 'past'
    
    return None

def handle_volunteer_questions(question_lower):
    """Gère intelligemment toutes les questions sur les volontaires"""
    
    # Patterns pour les niveaux d'activité
    if any(word in question_lower for word in ['non actif', 'inactif', 'pas actif', 'peu actif']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience ?medicalConditions
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
            FILTER(REGEX(?activityLevel, "non actif|inactif|peu actif", "i"))
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        }
        ORDER BY ?label
        """
    
    elif any(word in question_lower for word in ['très actif', 'very active', 'très actifs']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience ?medicalConditions
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
            FILTER(REGEX(?activityLevel, "très actif", "i"))
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        }
        ORDER BY ?label
        """
    
    elif any(word in question_lower for word in ['actif', 'active', 'actifs']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience ?medicalConditions
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
            FILTER(REGEX(?activityLevel, "actif", "i"))
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
        }
        ORDER BY ?label
        """
    
    # Patterns pour les compétences
    elif any(word in question_lower for word in ['compétence', 'skill', 'compétences', 'skills', 'domaine', 'savoir']):
        # Extraire le domaine de compétence si mentionné
        skill_keywords = ['programmation', 'informatique', 'langue', 'communication', 'gestion', 'technique', 'médical', 'scientifique']
        skill_filter = ""
        for skill in skill_keywords:
            if skill in question_lower:
                skill_filter = f'FILTER(REGEX(?skills, "{skill}", "i"))'
                break
        
        return f"""
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?experience ?motivation
        WHERE {{
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills .
            
            OPTIONAL {{ ?volunteer rdfs:label ?label . }}
            OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }}
            OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }}
            OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }}
            OPTIONAL {{ ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }}
            {skill_filter}
        }}
        ORDER BY ?skills
        """
    
    # Patterns pour l'expérience
    elif any(word in question_lower for word in ['expérience', 'experience', 'expérimenté', 'expérimentés', 'ancien', 'vétéran']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?experience ?skills ?activityLevel ?motivation
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience .
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
        }
        ORDER BY ?label
        """
    
    # Patterns pour les conditions médicales
    elif any(word in question_lower for word in ['médical', 'medical', 'condition', 'handicap', 'restriction', 'santé']):
        if any(word in question_lower for word in ['sans', 'pas de', 'aucune']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                FILTER NOT EXISTS { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            }
            ORDER BY ?label
            """
        else:
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience ?medicalConditions
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions .
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            }
            ORDER BY ?label
            """
    
    # Patterns pour la motivation
    elif any(word in question_lower for word in ['motivation', 'motivé', 'motivés', 'intérêt', 'passion']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?motivation ?generalMotivation ?skills ?activityLevel ?experience
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation .
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
        }
        ORDER BY ?label
        """
    
    # Patterns pour les contacts
    elif any(word in question_lower for word in ['contact', 'téléphone', 'phone', 'numéro', 'email', 'courriel']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?user
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone .
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        }
        ORDER BY ?label
        """
    
    # Patterns pour les statistiques
    elif any(word in question_lower for word in ['combien', 'nombre', 'total', 'statistique', 'stats', 'répartition']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT 
            (COUNT(?volunteer) as ?total)
            (COUNT(?active) as ?active_count)
            (COUNT(?experienced) as ?experienced_count)
            (COUNT(?with_skills) as ?with_skills_count)
            (COUNT(?with_medical) as ?with_medical_count)
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            
            OPTIONAL { 
                ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
                FILTER(REGEX(?activityLevel, "actif", "i"))
                BIND(?volunteer as ?active)
            }
            OPTIONAL { 
                ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience .
                BIND(?volunteer as ?experienced)
            }
            OPTIONAL { 
                ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills .
                BIND(?volunteer as ?with_skills)
            }
            OPTIONAL { 
                ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions .
                BIND(?volunteer as ?with_medical)
            }
        }
        """
    
    # Requête générale pour tous les volontaires
    else:
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience ?medicalConditions ?generalMotivation ?user
        WHERE {
            ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
            
            OPTIONAL { ?volunteer rdfs:label ?label . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9F95BAS8WtbTv8ZGBaPe42> ?medicalConditions . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RXzg1eKoCWK7S9zHsFoTFC> ?generalMotivation . }
            OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?user . }
        }
        ORDER BY ?label
        LIMIT 20
        """

def handle_assignment_questions(question_lower):
    """Gère intelligemment toutes les questions sur les assignements - Version avancée"""
    
    # Patterns pour les statuts - Plus de variations
    if any(word in question_lower for word in ['approuvé', 'approved', 'validé', 'accepté', 'confirmé', 'accepté', 'validé']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
            FILTER(REGEX(?status, "approuvé|approved|validé|accepté|confirmé", "i"))
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?startDate DESC
        """
    
    elif any(word in question_lower for word in ['rejeté', 'rejected', 'refusé', 'non approuvé', 'refusé', 'décliné', 'annulé']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
            FILTER(REGEX(?status, "non approuvé|rejeté|rejected|refusé|décliné|annulé", "i"))
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?startDate DESC
        """
    
    # Patterns pour les notes/évaluations - Plus intelligents
    elif any(word in question_lower for word in ['note', 'rating', 'évaluation', 'score', 'étoile', 'étoiles', 'notation', 'appréciation']):
        # Extraire la note minimale si mentionnée
        rating_filter = ""
        rating_condition = ""
        
        # Détection des plages de notes
        if '5 étoile' in question_lower or '5 étoiles' in question_lower or 'note 5' in question_lower:
            rating_filter = 'FILTER(?rating = 5)'
        elif '4 étoile' in question_lower or '4 étoiles' in question_lower or 'note 4' in question_lower:
            rating_filter = 'FILTER(?rating >= 4)'
        elif '3 étoile' in question_lower or '3 étoiles' in question_lower or 'note 3' in question_lower:
            rating_filter = 'FILTER(?rating >= 3)'
        elif '2 étoile' in question_lower or '2 étoiles' in question_lower or 'note 2' in question_lower:
            rating_filter = 'FILTER(?rating >= 2)'
        elif '1 étoile' in question_lower or '1 étoiles' in question_lower or 'note 1' in question_lower:
            rating_filter = 'FILTER(?rating >= 1)'
        elif 'et plus' in question_lower or 'et plus' in question_lower:
            # Détection automatique de la note de base
            for i in range(1, 6):
                if f'{i} étoile' in question_lower:
                    rating_filter = f'FILTER(?rating >= {i})'
                    break
        
        # Détection des notes élevées
        if any(word in question_lower for word in ['élevé', 'élevée', 'élevés', 'élevées', 'haute', 'haut', 'excellent', 'excellente']):
            rating_filter = 'FILTER(?rating >= 4)'
        elif any(word in question_lower for word in ['faible', 'faibles', 'basse', 'bas', 'mauvaise', 'mauvais']):
            rating_filter = 'FILTER(?rating <= 2)'
        
        return f"""
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {{
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
            
            OPTIONAL {{ ?assignment rdfs:label ?label . }}
            OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }}
            OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }}
            OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }}
            OPTIONAL {{ ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }}
            {rating_filter}
        }}
        ORDER BY DESC(?rating)
        """
    
    # Patterns pour les dates - Plus de variations
    elif any(word in question_lower for word in ['récent', 'recent', 'nouveau', 'nouveaux', 'dernier', 'derniers', 'récemment', 'récentes']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate .
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY DESC(?startDate)
        LIMIT 10
        """
    
    # Patterns pour les dates spécifiques
    elif any(word in question_lower for word in ['aujourd\'hui', 'today', 'ce jour', 'maintenant']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate .
            FILTER (xsd:date(?startDate) = xsd:date(NOW()))
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?startDate
        """
    
    elif any(word in question_lower for word in ['cette semaine', 'this week', 'semaine actuelle']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate .
            FILTER (?startDate >= NOW() && ?startDate <= (NOW() + "P7D"^^xsd:duration))
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?startDate
        """
    
    # Patterns pour les statistiques - Plus détaillées
    elif any(word in question_lower for word in ['combien', 'nombre', 'total', 'statistique', 'stats', 'répartition', 'bilan', 'compte', 'quantité']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        
        SELECT 
            (COUNT(?assignment) as ?total)
            (COUNT(?approved) as ?approved_count)
            (COUNT(?rejected) as ?rejected_count)
            (COUNT(?high_rated) as ?high_rated_count)
            (AVG(?rating) as ?average_rating)
            (MAX(?rating) as ?max_rating)
            (MIN(?rating) as ?min_rating)
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            
            OPTIONAL { 
                ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                FILTER(REGEX(?status, "approuvé|approved|validé|accepté|confirmé", "i"))
                BIND(?assignment as ?approved)
            }
            OPTIONAL { 
                ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                FILTER(REGEX(?status, "non approuvé|rejeté|rejected|refusé|décliné|annulé", "i"))
                BIND(?assignment as ?rejected)
            }
            OPTIONAL { 
                ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
                FILTER(?rating >= 4)
                BIND(?assignment as ?high_rated)
            }
        }
        """
    
    # Patterns pour les volontaires spécifiques - Plus intelligents
    elif any(word in question_lower for word in ['volontaire', 'volunteer', 'de', 'par', 'assigné à', 'assigné par']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer .
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?volunteer ?startDate DESC
        """
    
    # Patterns pour les événements - Plus intelligents
    elif any(word in question_lower for word in ['événement', 'event', 'évènement', 'activité', 'mission', 'tâche']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event .
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?event ?startDate DESC
        """
    
    # Patterns pour les performances
    elif any(word in question_lower for word in ['performance', 'performant', 'performants', 'meilleur', 'meilleurs', 'excellent', 'excellents']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
            FILTER(?rating >= 4)
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        }
        ORDER BY DESC(?rating)
        """
    
    # Patterns pour les problèmes
    elif any(word in question_lower for word in ['problème', 'problèmes', 'difficulté', 'difficultés', 'mauvais', 'mauvaise', 'faible', 'faibles']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            {
                ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
                FILTER(?rating <= 2)
            }
            UNION
            {
                ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                FILTER(REGEX(?status, "non approuvé|rejeté|rejected|refusé|décliné|annulé", "i"))
            }
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?rating ASC
        """
    
    # Patterns pour les assignements en attente
    elif any(word in question_lower for word in ['attente', 'pending', 'en cours', 'en attente', 'en attente de']):
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
            FILTER(REGEX(?status, "en attente|pending|en cours|en attente de", "i"))
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?startDate
        """
    
    # Requête générale pour tous les assignements
    else:
        return """
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?assignment ?label ?volunteer ?event ?startDate ?status ?rating
        WHERE {
            ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
            
            OPTIONAL { ?assignment rdfs:label ?label . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBqttmTqH5uyTK64wj0hDiD> ?event . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
        }
        ORDER BY ?assignment
        LIMIT 20
        """

def transform_question_to_sparql_combined(question):
    """Transforme une question en français en requête SPARQL - Version combinée et intelligente"""
    question_lower = question.lower()
    
    # QUESTIONS SUR LES VOLONTAIRES - PRIORITÉ ABSOLUE
    if any(word in question_lower for word in ['volontaire', 'volunteer', 'bénévole', 'benevole']):
        return handle_volunteer_questions(question_lower)
    
    # QUESTIONS SUR LES ASSIGNEMENTS - PRIORITÉ ABSOLUE
    elif any(word in question_lower for word in ['assignement', 'assignment', 'assignation', 'affectation']):
        return handle_assignment_questions(question_lower)
    
    # QUESTIONS SUR LES CAMPAGNES
    elif any(word in question_lower for word in ["campagne", "campaign"]):
        if any(word in question_lower for word in ["actif", "active", "en cours", "current"]):
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
            WHERE {
                {
                    ?campaign a eco:Campaign .
                }
                UNION
                {
                    ?subClass rdfs:subClassOf* eco:Campaign .
                    ?campaign a ?subClass .
                }
                ?campaign eco:campaignName ?name .
                ?campaign eco:campaignStatus ?status .
                FILTER(LCASE(STR(?status)) = "active" || LCASE(STR(?status)) = "actif" || LCASE(STR(?status)) = "en cours")
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { 
                    ?campaign a ?type .
                    FILTER(?type != eco:Campaign)
                }
            }
            ORDER BY ?name
            """
        
        elif "nettoyage" in question_lower or "cleanup" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal
            WHERE {
                ?campaign a eco:CleanupCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
            }
            ORDER BY ?name
            """
        
        elif "sensibilisation" in question_lower or "awareness" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal
            WHERE {
                ?campaign a eco:AwarenessCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
            }
            ORDER BY ?name
            """
        
        elif "financement" in question_lower or "funding" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?targetAmount ?fundsRaised
            WHERE {
                ?campaign a eco:FundingCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { ?campaign eco:targetAmount ?targetAmount }
                OPTIONAL { ?campaign eco:fundsRaised ?fundsRaised }
            }
            ORDER BY ?name
            """
        
        elif "événement" in question_lower or "event" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?targetParticipants
            WHERE {
                ?campaign a eco:EventCampaign .
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { ?campaign eco:targetParticipants ?targetParticipants }
            }
            ORDER BY ?name
            """
        
        else:
            # Requête générale pour les campagnes
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?description ?status ?startDate ?endDate ?goal ?type
            WHERE {
                {
                    ?campaign a eco:Campaign .
                }
                UNION
                {
                    ?subClass rdfs:subClassOf* eco:Campaign .
                    ?campaign a ?subClass .
                }
                ?campaign eco:campaignName ?name .
                OPTIONAL { ?campaign eco:campaignDescription ?description }
                OPTIONAL { ?campaign eco:campaignStatus ?status }
                OPTIONAL { ?campaign eco:startDate ?startDate }
                OPTIONAL { ?campaign eco:endDate ?endDate }
                OPTIONAL { ?campaign eco:goal ?goal }
                OPTIONAL { 
                    ?campaign a ?type .
                    FILTER(?type != eco:Campaign)
                }
            }
            ORDER BY ?name
            LIMIT 20
            """
    
    # QUESTIONS SUR LES RESSOURCES
    elif any(word in question_lower for word in ["ressource", "resource"]):
        if "humaine" in question_lower or "human" in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            
            SELECT ?name ?description ?category ?quantity ?unitCost ?skillLevel
            WHERE {
                ?resource a eco:HumanResource .
                ?resource eco:resourceName ?name .
                OPTIONAL { ?resource eco:resourceDescription ?description }
                OPTIONAL { ?resource eco:resourceCategory ?category }
                OPTIONAL { ?resource eco:quantityAvailable ?quantity }
                OPTIONAL { ?resource eco:unitCost ?unitCost }
                OPTIONAL { ?resource eco:skillLevel ?skillLevel }
            }
            ORDER BY ?name
            """

    # QUESTIONS SUR LES SPONSORS ET DONATIONS
    elif any(word in question_lower for word in ['sponsor', 'sponsors', 'sponsorship', 'sponsorships', 'donation', 'donations', 'donateur', 'donateurs', 'commanditaire', 'entreprise', 'entreprises']):
        # Try to extract a sponsorship level term first (e.g., "niveau Gold", "sponsorshipLevel Gold")
        level_match = re.search(r"(?:niveau|sponsorshiplevel|sponsorship level|level)\s+(?:de\s+)?([a-z0-9_\- ]+)", question_lower)
        if level_match:
            term = level_match.group(1).strip()
            term = term.strip("\"' .?/,;:")
            term_lower = term.lower()
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring)
            WHERE {{
                ?sponsor a eco:Sponsor .
                OPTIONAL {{ ?sponsor eco:companyName ?companyName }}
                OPTIONAL {{ ?sponsor eco:industry ?industry }}
                OPTIONAL {{ ?sponsor eco:contactEmail ?contactEmail }}
                OPTIONAL {{ ?sponsor eco:phoneNumber ?phoneNumber }}
                OPTIONAL {{ ?sponsor eco:website ?website }}
                OPTIONAL {{ ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL {{ ?level eco:levelName ?levelName }} }}
                FILTER(CONTAINS(LCASE(STR(?levelName)), "{term_lower}"))
            }}
            ORDER BY ?companyName
            LIMIT 100
            """

        # Try to extract an industry/sector term from the question (e.g., "industrie GreenTechnology")
        industry_match = re.search(r"(?:industrie|secteur|industry)\s+([a-z0-9_\- ]+)", question_lower)
        if industry_match:
            term = industry_match.group(1).strip()
            # sanitize term
            term = term.strip("\"' .?/,;:")
            term_lower = term.lower()
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring)
            WHERE {{
                ?sponsor a eco:Sponsor .
                OPTIONAL {{ ?sponsor eco:companyName ?companyName }}
                OPTIONAL {{ ?sponsor eco:industry ?industry }}
                OPTIONAL {{ ?sponsor eco:contactEmail ?contactEmail }}
                OPTIONAL {{ ?sponsor eco:phoneNumber ?phoneNumber }}
                OPTIONAL {{ ?sponsor eco:website ?website }}
                OPTIONAL {{ ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL {{ ?level eco:levelName ?levelName }} }}
                FILTER(CONTAINS(LCASE(STR(?industry)), "{term_lower}"))
            }}
            ORDER BY ?companyName
            """

        # General sponsor query (no specific industry filter)
        # If the question explicitly asks for sponsors/entreprises who made donations,
        # return only sponsors that have made donations by joining on eco:makesDonation.
        if any(word in question_lower for word in ['sponsor', 'sponsors', 'parrain', 'commanditaire', 'commanditaires', 'entreprise', 'entreprises']):
            # If the question also mentions donations, filter sponsors to those who made donations
            if any(word in question_lower for word in ['donation', 'donations', 'donateur', 'donateurs', 'fund', 'funds', 'finance', 'financement', 'fonds']):
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT DISTINCT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring) ?donation
                WHERE {
                    ?sponsor a eco:Sponsor .
                    ?sponsor eco:makesDonation ?donation .
                    OPTIONAL { ?sponsor eco:companyName ?companyName }
                    OPTIONAL { ?sponsor eco:industry ?industry }
                    OPTIONAL { ?sponsor eco:contactEmail ?contactEmail }
                    OPTIONAL { ?sponsor eco:phoneNumber ?phoneNumber }
                    OPTIONAL { ?sponsor eco:website ?website }
                    OPTIONAL { ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL { ?level eco:levelName ?levelName } }
                    OPTIONAL { ?donation eco:amount ?amount }
                    OPTIONAL { ?donation eco:currency ?currency }
                    OPTIONAL { ?donation eco:dateDonated ?date }
                }
                ORDER BY ?companyName
                LIMIT 200
                """

            # Otherwise return all sponsors (no donation filter)
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?sponsor (?companyName AS ?nomEntreprise) (?industry AS ?secteur) (?contactEmail AS ?courriel) (?phoneNumber AS ?telephone) (?website AS ?siteWeb) (?levelName AS ?niveauDeSponsoring)
            WHERE {
                ?sponsor a eco:Sponsor .
                OPTIONAL { ?sponsor eco:companyName ?companyName }
                OPTIONAL { ?sponsor eco:industry ?industry }
                OPTIONAL { ?sponsor eco:contactEmail ?contactEmail }
                OPTIONAL { ?sponsor eco:phoneNumber ?phoneNumber }
                OPTIONAL { ?sponsor eco:website ?website }
                OPTIONAL { ?sponsor eco:hasSponsorshipLevel ?level . OPTIONAL { ?level eco:levelName ?levelName } }
            }
            ORDER BY ?companyName
            LIMIT 100
            """

        # Donations summary or donations to a specific event
        elif any(word in question_lower for word in ['fund', 'funds', 'funded', 'finance', 'financement', 'fonds', 'donation', 'donations', 'donateur', 'donateurs']):
            # Look for an explicit donation type (e.g., 'de type FinancialDonation' or 'type financial')
            type_match = re.search(r"(?:type|de type)\s+([A-Za-z0-9_\-]+)", question_lower)
            if type_match:
                raw = type_match.group(1).strip()
                token = raw.strip("\"' .?/,;:")
                token_lower = token.lower()

                # common synonyms mapping (token -> class local name)
                type_map = {
                    'financial': 'FinancialDonation', 'financiere': 'FinancialDonation', 'financière': 'FinancialDonation', 'financialdonation': 'FinancialDonation', 'financialdonations': 'FinancialDonation',
                    'material': 'MaterialDonation', 'materialdonation': 'MaterialDonation', 'materialdonations': 'MaterialDonation', 'matériel': 'MaterialDonation', 'materiel': 'MaterialDonation',
                    'service': 'ServiceDonation', 'servicedonation': 'ServiceDonation', 'services': 'ServiceDonation'
                }

                # If token directly matches a mapped class, use the class IRI filter
                if token_lower in type_map:
                    class_name = type_map[token_lower]
                    return f"""
                    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                    SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) (?donorName AS ?donateur) ?date
                    WHERE {{
                        ?donation a eco:{class_name} .
                        OPTIONAL {{ ?donation eco:amount ?amount }}
                        OPTIONAL {{ ?donation eco:currency ?currency }}
                        OPTIONAL {{ ?donation eco:dateDonated ?date }}
                        OPTIONAL {{ ?donation ^eco:makesDonation ?donor . OPTIONAL {{ ?donor eco:companyName ?donorName }} }}
                    }}
                    ORDER BY DESC(?date)
                    LIMIT 200
                    """
                # If token looks like a class local name already (e.g., FinancialDonation)
                if re.match(r'^[A-Za-z]+Donation$', token):
                    class_name = token
                    return f"""
                    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                    SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) (?donorName AS ?donateur) ?date
                    WHERE {{
                        ?donation a eco:{class_name} .
                        OPTIONAL {{ ?donation eco:amount ?amount }}
                        OPTIONAL {{ ?donation eco:currency ?currency }}
                        OPTIONAL {{ ?donation eco:dateDonated ?date }}
                        OPTIONAL {{ ?donation ^eco:makesDonation ?donor . OPTIONAL {{ ?donor eco:companyName ?donorName }} }}
                    }}
                    ORDER BY DESC(?date)
                    LIMIT 200
                    """
                # Otherwise, try matching by rdfs:label on the donation's class
                token_esc = token_lower.replace('"','')
                return f"""
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) (?donorName AS ?donateur) ?date
                WHERE {{
                    ?donation a ?type .
                    ?type rdfs:label ?typeLabel .
                    FILTER(CONTAINS(LCASE(STR(?typeLabel)), "{token_esc}"))
                    OPTIONAL {{ ?donation eco:amount ?amount }}
                    OPTIONAL {{ ?donation eco:currency ?currency }}
                    OPTIONAL {{ ?donation eco:dateDonated ?date }}
                    OPTIONAL {{ ?donation ^eco:makesDonation ?donor . OPTIONAL {{ ?donor eco:companyName ?donorName }} }}
                }}
                ORDER BY DESC(?date)
                LIMIT 200
                """

            # If not a type-specific question, check for event-scoped donations
            if any(word in question_lower for word in ['event', 'événement', 'à', 'to']):
                # Return only events that have donations. Group donations by event and provide counts and last donation date.
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                SELECT ?event ?eventTitle (COUNT(?donation) AS ?donationCount) (MAX(?date) AS ?lastDonation)
                WHERE {
                    ?donation a ?type .
                    FILTER(?type = eco:Donation || ?type = eco:FinancialDonation || ?type = eco:MaterialDonation || ?type = eco:ServiceDonation)
                    ?donation eco:fundsEvent ?event .
                    ?event eco:eventTitle ?eventTitle .
                    OPTIONAL { ?donation eco:dateDonated ?date }
                }
                GROUP BY ?event ?eventTitle
                ORDER BY DESC(?donationCount)
                LIMIT 200
                """

            else:
                # General donations list (alias French labels) - only common donation classes
                return """
                PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
                SELECT ?donation ?type (?amount AS ?montant) (?currency AS ?devise) (?donorName AS ?donateur) ?date
                WHERE {
                    ?donation a ?type .
                    FILTER(?type = eco:Donation || ?type = eco:FinancialDonation || ?type = eco:MaterialDonation || ?type = eco:ServiceDonation)
                    OPTIONAL { ?donation eco:amount ?amount }
                    OPTIONAL { ?donation eco:currency ?currency }
                    OPTIONAL { ?donation eco:dateDonated ?date }
                    OPTIONAL {
                        ?donation ^eco:makesDonation ?donor .
                        OPTIONAL { ?donor eco:companyName ?donorName }
                    }
                }
                ORDER BY ?date
                LIMIT 50
                """
    
    # QUESTIONS SUR LES UTILISATEURS
    elif "utilisateur" in question_lower or "user" in question_lower:
        return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        
        SELECT ?firstName ?lastName ?email ?role ?registrationDate
        WHERE {
            ?user a eco:User .
            ?user eco:firstName ?firstName .
            OPTIONAL { ?user eco:lastName ?lastName }
            OPTIONAL { ?user eco:email ?email }
            OPTIONAL { ?user eco:role ?role }
            OPTIONAL { ?user eco:registrationDate ?registrationDate }
        }
        ORDER BY ?firstName
        LIMIT 20
        """
    
    # QUESTIONS SUR LES RÉSERVATIONS (priorité sur les événements)
    elif any(word in question_lower for word in ['réservation', 'reservation', 'réserver', 'booking']) or 'réservation' in question_lower:
        if 'confirmé' in question_lower or 'confirmed' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
            WHERE {
                ?reservation a eco:Reservation .
                ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
                FILTER(LCASE(STR(?status)) = "confirmed")
                OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }
                OPTIONAL { 
                    ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                    ?event eco:eventTitle ?eventTitle .
                }
                OPTIONAL { 
                    ?reservation eco:belongsToUser ?user .
                    ?user eco:firstName ?userName .
                    OPTIONAL { ?user eco:email ?userEmail . }
                }
            }
            ORDER BY ?reservation
            """
        elif 'attente' in question_lower or 'pending' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
            WHERE {
                ?reservation a eco:Reservation .
                ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
                FILTER(LCASE(STR(?status)) = "pending")
                OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }
                OPTIONAL { 
                    ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                    ?event eco:eventTitle ?eventTitle .
                }
                OPTIONAL { 
                    ?reservation eco:belongsToUser ?user .
                    ?user eco:firstName ?userName .
                    OPTIONAL { ?user eco:email ?userEmail . }
                }
            }
            ORDER BY ?reservation
            """
        elif 'annulé' in question_lower or 'cancelled' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
            WHERE {
                ?reservation a eco:Reservation .
                ?reservation webprotege:R9wdyKGFoajnFCFN4oqnwHr ?status .
                FILTER(LCASE(STR(?status)) = "cancelled")
                OPTIONAL { ?reservation webprotege:R7QgAmvOpBSpwRmRrDZL8VE ?seatNumber . }
                OPTIONAL { 
                    ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                    ?event eco:eventTitle ?eventTitle .
                }
                OPTIONAL { 
                    ?reservation eco:belongsToUser ?user .
                    ?user eco:firstName ?userName .
                    OPTIONAL { ?user eco:email ?userEmail . }
                }
            }
            ORDER BY ?reservation
            """
        elif 'par événement' in question_lower or 'par event' in question_lower or 'groupé' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?eventTitle (COUNT(?reservation) as ?reservationCount) ?eventDate ?locationName
            WHERE {
                ?reservation a eco:Reservation .
                ?reservation webprotege:R8r5yxVXnZfa0TwP5biVHiL ?event .
                ?event eco:eventTitle ?eventTitle .
                OPTIONAL { ?event eco:eventDate ?eventDate . }
                OPTIONAL { 
                    ?event eco:isLocatedAt ?location .
                    ?location eco:locationName ?locationName .
                }
            }
            GROUP BY ?eventTitle ?eventDate ?locationName
            ORDER BY ?eventTitle
            """
        else:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?reservation ?seatNumber ?status ?eventTitle ?userName ?userEmail
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
            }
            ORDER BY ?reservation
            """

    # QUESTIONS SUR LES ÉVÉNEMENTS - COMPREHENSIVE VERSION
    elif any(word in question_lower for word in ['événement', 'event', 'évènement', 'evenement', 'événements', 'events']):
        city_name = extract_city_from_question(question_lower)
        date_filter = extract_date_from_question(question_lower)
        
        # Build city filter if city is mentioned
        city_filter = ""
        if city_name:
            city_filter = f'FILTER (LCASE(STR(?city)) = "{city_name.lower()}" || CONTAINS(LCASE(STR(?city)), "{city_name.lower()}"))'
        
        # Build date filter based on time period
        date_condition = ""
        if date_filter == 'today':
            date_condition = 'FILTER (xsd:date(?date) = xsd:date(NOW()))'
        elif date_filter == 'tomorrow':
            date_condition = 'FILTER (xsd:date(?date) = xsd:date(NOW() + "P1D"^^xsd:duration))'
        elif date_filter == 'this_week':
            date_condition = 'FILTER (?date >= NOW() && ?date <= (NOW() + "P7D"^^xsd:duration))'
        elif date_filter == 'weekend':
            date_condition = 'FILTER (?date >= NOW() && ?date <= (NOW() + "P7D"^^xsd:duration)) FILTER (DAY(?date) IN (6, 7))'
        elif date_filter == 'this_month':
            date_condition = 'FILTER (?date >= NOW() && ?date <= (NOW() + "P30D"^^xsd:duration))'
        elif date_filter == 'future':
            date_condition = 'FILTER (?date >= NOW())'
        elif date_filter == 'past':
            date_condition = 'FILTER (?date < NOW())'
        
        # TOUS LES ÉVÉNEMENTS (avec filtres optionnels)
        if any(word in question_lower for word in ['tous', 'all', 'every', 'liste complète', 'complete list']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription ?organizerName ?eventType
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                OPTIONAL {{ ?event eco:maxParticipants ?maxParticipants . }}
                OPTIONAL {{ 
                    ?event eco:isOrganizedBy ?organizer .
                    ?organizer eco:firstName ?firstName .
                    ?organizer eco:lastName ?lastName .
                    BIND(CONCAT(?firstName, " ", ?lastName) AS ?organizerName)
                }}
                OPTIONAL {{
                    ?event a ?eventType .
                    FILTER(?eventType != eco:Event)
                }}
                {city_filter}
                {date_condition if date_condition else ''}
            }}
            ORDER BY ?date
            LIMIT 30
            """
        
        # ÉVÉNEMENTS À VENIR / FUTURS
        elif any(word in question_lower for word in ['à venir', 'futur', 'future', 'upcoming', 'prochain']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                FILTER (?date >= NOW())
                {city_filter}
            }}
            ORDER BY ?date
            LIMIT 20
            """
        
        # ÉVÉNEMENTS PASSÉS
        elif any(word in question_lower for word in ['passé', 'past', 'ancien', 'previous', 'terminé']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                FILTER (?date < NOW())
                {city_filter}
            }}
            ORDER BY DESC(?date)
            LIMIT 15
            """
        
        # ÉVÉNEMENTS PAR TYPE
        elif any(word in question_lower for word in ['éducatif', 'educatif', 'educational', 'formation']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:EducationalEvent ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                {city_filter}
                {date_condition if date_condition else 'FILTER (?date >= NOW())'}
            }}
            ORDER BY ?date
            """
        
        elif any(word in question_lower for word in ['compétitif', 'competitif', 'competitive', 'compétition']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:CompetitiveEvent ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                {city_filter}
                {date_condition if date_condition else 'FILTER (?date >= NOW())'}
            }}
            ORDER BY ?date
            """
        
        elif any(word in question_lower for word in ['divertissement', 'entertainment', 'loisir', 'recreation']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:EntertainmentEvent ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                {city_filter}
                {date_condition if date_condition else 'FILTER (?date >= NOW())'}
            }}
            ORDER BY ?date
            """
        
        elif any(word in question_lower for word in ['social', 'socialisation', 'networking']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?maxParticipants ?eventDescription
            WHERE {{
                ?event a eco:SocializationEvent ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?eventDescription . }}
                {city_filter}
                {date_condition if date_condition else 'FILTER (?date >= NOW())'}
            }}
            ORDER BY ?date
            """
        
        # QUESTIONS SUR LA LOCALISATION
        elif any(word in question_lower for word in ['où', 'where', 'lieu', 'location', 'endroit', 'place', 'adresse']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?location ?locationName ?address ?city ?date
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName ;
                     eco:address ?address .
                OPTIONAL {{ ?loc eco:city ?city . }}
                {city_filter}
            }}
            ORDER BY ?date
            """
        
        # QUESTIONS SUR LES DATES
        elif any(word in question_lower for word in ['quand', 'when', 'date', 'heure', 'time', 'début', 'start']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName ?city ?duration
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:duration ?duration . }}
                {city_filter}
            }}
            ORDER BY ?date
            """
        
        # QUESTIONS SUR LES ORGANISATEURS
        elif any(word in question_lower for word in ['qui organise', 'organisateur', 'organizer', 'organise', 'organisé par']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?organizer ?firstName ?lastName ?email ?phone ?city
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:isOrganizedBy ?organizer .
                ?organizer eco:firstName ?firstName ;
                          eco:lastName ?lastName .
                OPTIONAL {{ ?organizer eco:email ?email . }}
                OPTIONAL {{ ?organizer eco:phone ?phone . }}
                OPTIONAL {{
                    ?event eco:isLocatedAt ?loc .
                    ?loc eco:city ?city .
                }}
                {city_filter}
            }}
            ORDER BY ?lastName ?firstName
            """
        
        # REQUÊTE GÉNÉRALE POUR LES ÉVÉNEMENTS (avec filtres combinés)
        else:
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?description ?date ?locationName ?city ?maxParticipants ?organizerName
            WHERE {{
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName .
                OPTIONAL {{ ?loc eco:city ?city . }}
                OPTIONAL {{ ?event eco:eventDescription ?description . }}
                OPTIONAL {{ ?event eco:maxParticipants ?maxParticipants . }}
                OPTIONAL {{ 
                    ?event eco:isOrganizedBy ?organizer .
                    ?organizer eco:firstName ?firstName .
                    ?organizer eco:lastName ?lastName .
                    BIND(CONCAT(?firstName, " ", ?lastName) AS ?organizerName)
                }}
                {city_filter}
                {date_condition if date_condition else 'FILTER (?date >= NOW())'}
            }}
            ORDER BY ?date
            LIMIT 20
            """
    
    # QUESTIONS SUR LES LOCATIONS
    elif any(word in question_lower for word in ['location', 'lieu', 'endroit', 'salle', 'place', 'venue', 'local', 'site']):
        city_name = extract_city_from_question(question_lower)
        
        # Build city filter if city is mentioned
        city_filter = ""
        if city_name:
            city_filter = f'FILTER (LCASE(STR(?city)) = "{city_name.lower()}" || CONTAINS(LCASE(STR(?city)), "{city_name.lower()}"))'
        
        # LOCATIONS DISPONIBLES
        if any(word in question_lower for word in ['disponible', 'available', 'libre', 'free', 'vacant']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?country ?capacity ?price ?description ?locationType
            WHERE {{
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:country ?country . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                OPTIONAL {{ ?location eco:reserved ?reserved . }}
                OPTIONAL {{ ?location eco:inRepair ?inRepair . }}
                OPTIONAL {{
                    ?location a ?locationType .
                    FILTER(?locationType != eco:Location)
                }}
                FILTER (!BOUND(?reserved) || ?reserved = "false" || LCASE(STR(?reserved)) = "false")
                FILTER (!BOUND(?inRepair) || ?inRepair = "false" || LCASE(STR(?inRepair)) = "false")
                {city_filter}
            }}
            ORDER BY ?name
            """
        
        # LOCATIONS PAR CAPACITÉ
        elif any(word in question_lower for word in ['capacité', 'capacity', 'taille', 'size', 'grand', 'small', 'petit']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price ?description
            WHERE {{
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                {city_filter}
            }}
            ORDER BY DESC(?capacity)
            """
        
        # LOCATIONS PAR PRIX
        elif any(word in question_lower for word in ['prix', 'price', 'coût', 'cost', 'tarif', 'fee', 'gratuit', 'free']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price ?description
            WHERE {{
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                FILTER (BOUND(?price))
                {city_filter}
            }}
            ORDER BY ?price
            """
        
        # LOCATIONS RÉSERVÉES
        elif any(word in question_lower for word in ['réservé', 'reserved', 'occupé', 'booked', 'indisponible']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price ?reserved ?inRepair
            WHERE {{
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:reserved ?reserved . }}
                OPTIONAL {{ ?location eco:inRepair ?inRepair . }}
                FILTER (BOUND(?reserved) && (?reserved = "true" || LCASE(STR(?reserved)) = "true") || 
                        BOUND(?inRepair) && (?inRepair = "true" || LCASE(STR(?inRepair)) = "true"))
                {city_filter}
            }}
            ORDER BY ?name
            """
        
        # LOCATIONS PAR TYPE
        elif any(word in question_lower for word in ['intérieur', 'indoor', 'intérieure']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price ?description
            WHERE {{
                ?location a eco:Indoor ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                {city_filter}
            }}
            ORDER BY ?name
            """
        
        elif any(word in question_lower for word in ['extérieur', 'outdoor', 'extérieure', 'plein air']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price ?description
            WHERE {{
                ?location a eco:Outdoor ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                {city_filter}
            }}
            ORDER BY ?name
            """
        
        elif any(word in question_lower for word in ['virtuel', 'virtual', 'en ligne', 'online']):
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?platformURL ?capacity ?price ?description
            WHERE {{
                ?location a eco:VirtualPlatform ;
                         eco:locationName ?name ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:platformURL ?platformURL . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
            }}
            ORDER BY ?name
            """
        
        # REQUÊTE GÉNÉRALE POUR LES LOCATIONS
        else:
            return f"""
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?country ?capacity ?price ?description ?reserved ?inRepair ?locationType
            WHERE {{
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity .
                OPTIONAL {{ ?location eco:city ?city . }}
                OPTIONAL {{ ?location eco:country ?country . }}
                OPTIONAL {{ ?location eco:price ?price . }}
                OPTIONAL {{ ?location eco:locationDescription ?description . }}
                OPTIONAL {{ ?location eco:reserved ?reserved . }}
                OPTIONAL {{ ?location eco:inRepair ?inRepair . }}
                OPTIONAL {{
                    ?location a ?locationType .
                    FILTER(?locationType != eco:Location)
                }}
                {city_filter}
            }}
            ORDER BY ?name
            LIMIT 20
            """
    
    # QUESTIONS SUR LES ORGANISATEURS ET UTILISATEURS (sans volontaires)
    elif any(word in question_lower for word in ['utilisateur', 'user', 'personne', 'organisateur']) and not any(word in question_lower for word in ['volontaire', 'volunteer', 'bénévole', 'benevole']):
        if 'organisateur' in question_lower or 'organise' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT DISTINCT ?user ?firstName ?lastName ?email ?phone
            WHERE {
                ?event a eco:Event ;
                       eco:isOrganizedBy ?user .
                ?user eco:firstName ?firstName ;
                      eco:lastName ?lastName ;
                      eco:email ?email .
                OPTIONAL { ?user eco:phone ?phone . }
            }
            ORDER BY ?lastName ?firstName
            """
        else:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?user ?firstName ?lastName ?email ?role ?registrationDate
            WHERE {
                ?user a eco:User ;
                      eco:firstName ?firstName ;
                      eco:lastName ?lastName ;
                      eco:email ?email ;
                      eco:role ?role .
                OPTIONAL { ?user eco:registrationDate ?registrationDate . }
            }
            ORDER BY ?lastName ?firstName
            """
    

    # QUESTIONS SUR LES CERTIFICATIONS
    elif any(word in question_lower for word in ['certification', 'certificat', 'diplôme', 'récompense', 'badge']):
        if 'participation' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
            WHERE {
                ?certification a eco:Certification .
                ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
                FILTER(CONTAINS(LCASE(STR(?type)), "participation"))
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                    OPTIONAL { ?issuer eco:email ?issuerEmail . }
                }
            }
            ORDER BY ?certification
            """
        elif 'accomplissement' in question_lower or 'achievement' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
            WHERE {
                ?certification a eco:Certification .
                ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
                FILTER(CONTAINS(LCASE(STR(?type)), "achievement"))
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                    OPTIONAL { ?issuer eco:email ?issuerEmail . }
                }
            }
            ORDER BY ?certification
            """
        elif 'par points' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?awardedToName ?issuerName
            WHERE {
                ?certification a eco:Certification .
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type . }
                OPTIONAL { 
                    ?certification eco:awardedTo ?recipient .
                    ?recipient eco:firstName ?awardedToName .
                }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                }
            }
            ORDER BY DESC(?pointsEarned)
            """
        elif 'points' in question_lower or 'eco-points' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
            WHERE {
                ?certification a eco:Certification .
                ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
                FILTER(CONTAINS(LCASE(STR(?type)), "points"))
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                    OPTIONAL { ?issuer eco:email ?issuerEmail . }
                }
            }
            ORDER BY DESC(?pointsEarned)
            """
        elif 'reçu' in question_lower or 'reçu' in question_lower or 'awarded' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?awardedToName ?awardedToEmail ?issuerName
            WHERE {
                ?certification a eco:Certification .
                ?certification eco:awardedTo ?recipient .
                ?recipient eco:firstName ?awardedToName .
                OPTIONAL { ?recipient eco:email ?awardedToEmail . }
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                }
            }
            ORDER BY ?awardedToName
            """
        elif 'types' in question_lower and ('certification' in question_lower or 'certificat' in question_lower):
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT DISTINCT ?type (COUNT(?certification) as ?count)
            WHERE {
                ?certification a eco:Certification .
                ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
            }
            GROUP BY ?type
            ORDER BY ?type
            """
        elif 'émet' in question_lower or 'émet' in question_lower or 'issuer' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT DISTINCT ?issuerName ?issuerEmail (COUNT(?certification) as ?certCount)
            WHERE {
                ?certification a eco:Certification .
                ?certification eco:issuedBy ?issuer .
                ?issuer eco:firstName ?issuerName .
                OPTIONAL { ?issuer eco:email ?issuerEmail . }
            }
            GROUP BY ?issuerName ?issuerEmail
            ORDER BY ?issuerName
            """
        elif 'leadership' in question_lower or 'leader' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
            WHERE {
                ?certification a eco:Certification .
                ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type .
                FILTER(CONTAINS(LCASE(STR(?type)), "leadership"))
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                    OPTIONAL { ?issuer eco:email ?issuerEmail . }
                }
            }
            ORDER BY ?certification
            """
        else:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT ?certification ?certificateCode ?pointsEarned ?type ?issuerName ?issuerEmail
            WHERE {
                ?certification a eco:Certification .
                OPTIONAL { ?certification webprotege:R9QGoktbkOBbsLkvgjicNA8 ?certificateCode . }
                OPTIONAL { ?certification webprotege:R9gsGMKtVBKEAd4d8I75UkC ?pointsEarned . }
                OPTIONAL { ?certification webprotege:RBPJvon09P5n1GLdLbu2esV ?type . }
                OPTIONAL { 
                    ?certification eco:issuedBy ?issuer .
                    ?issuer eco:firstName ?issuerName .
                    OPTIONAL { ?issuer eco:email ?issuerEmail . }
                }
            }
            ORDER BY ?certification
            """
    
    # REQUÊTE PAR DÉFAUT AMÉLIORÉE
    return """
    PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?name ?description ?type
    WHERE {
        {
            ?item a eco:Campaign .
            ?item eco:campaignName ?name .
            OPTIONAL { ?item eco:campaignDescription ?description }
            BIND("Campagne" as ?type)
        }
        UNION
        {
            ?item a eco:Resource .
            ?item eco:resourceName ?name .
            OPTIONAL { ?item eco:resourceDescription ?description }
            BIND("Ressource" as ?type)
        }
        UNION
        {
            ?item a eco:User .
            ?item eco:firstName ?name .
            OPTIONAL { ?item eco:lastName ?description }
            BIND("Utilisateur" as ?type)
        }
        UNION
        {
            ?item a eco:Sponsor .
            OPTIONAL { ?item eco:companyName ?name . }
            OPTIONAL { ?item eco:industry ?description . }
            BIND("Sponsor" as ?type)
        }
        UNION
        {
            ?item a eco:Event .
            ?item eco:eventTitle ?name .
            OPTIONAL { ?item eco:eventDescription ?description }
            BIND("Événement" as ?type)
        }
        UNION
        {
            ?item a eco:Location .
            ?item eco:locationName ?name .
            OPTIONAL { ?item eco:locationDescription ?description }
            BIND("Location" as ?type)
        }
    }
    ORDER BY ?type ?name
    LIMIT 20
    """