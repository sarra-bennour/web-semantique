from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
from modules.taln_service import TALNService
from modules.gemini_sparql_service import GeminiSPARQLTransformer

search_bp = Blueprint('search', __name__)

# Initialize services
taln_service = TALNService()
gemini_transformer = GeminiSPARQLTransformer()

@search_bp.route('/search', methods=['POST'])
def semantic_search():
    """Recherche sémantique - TALN → Gemini → SPARQL pipeline"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').lower()

        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🔍 Processing question: {question}")
        
        # Step 1: TALN Analysis - Extract entities, relationships, intent
        print("📝 Step 1: TALN Analysis...")
        taln_analysis = taln_service.analyze_question(question)
        print(f"✅ TALN Analysis completed. Entities: {len(taln_analysis.get('entities', []))}")
        
        # Step 2: Gemini SPARQL Generation - Generate query from TALN analysis
        print("🤖 Step 2: Gemini SPARQL Generation...")
        sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
        print(f"✅ SPARQL Query generated: {len(sparql_query)} characters")
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400
        
        # Step 3: Execute SPARQL Query
        print("⚡ Step 3: Executing SPARQL Query...")
        results = sparql_utils.execute_query(sparql_query)
        print(f"✅ Query executed. Results: {len(results) if results else 0} rows")
        
        # Return comprehensive response
        return jsonify({
            "question": question,
            "taln_analysis": taln_analysis,
            "sparql_query": sparql_query,
            "results": results,
            "pipeline_info": {
                "taln_confidence": taln_analysis.get('confidence_scores', {}).get('overall_confidence', 0.0),
                "entities_detected": len(taln_analysis.get('entities', [])),
                "intent_classified": taln_analysis.get('intent', {}).get('primary_intent', 'unknown'),
                "query_length": len(sparql_query),
                "results_count": len(results) if results else 0
            }
        })
        
    except Exception as e:
        print(f"❌ Error in semantic search pipeline: {str(e)}")
        return jsonify({"error": f"Erreur dans le pipeline de recherche: {str(e)}"}), 500

@search_bp.route('/search/ai', methods=['POST'])
def ai_search():
    """Recherche avec IA - Version alternative utilisant directement Gemini"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🤖 AI Search processing: {question}")
        
        # Direct Gemini transformation (fallback method)
        sparql_query = gemini_transformer.transform_question_to_sparql(question)
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400
        
        # Execute query
        results = sparql_utils.execute_query(sparql_query)
        
        return jsonify({
            "question": question,
            "sparql_query": sparql_query,
            "results": results,
            "method": "direct_gemini"
        })
        
    except Exception as e:
        print(f"❌ Error in AI search: {str(e)}")
        return jsonify({"error": f"Erreur dans la recherche IA: {str(e)}"}), 500

@search_bp.route('/search/hybrid', methods=['POST'])
def hybrid_search():
    """Recherche hybride - Combine TALN + Gemini + fallback"""
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question vide"}), 400
        
        print(f"🔄 Hybrid Search processing: {question}")
        
        # Try TALN + Gemini first
        try:
            taln_analysis = taln_service.analyze_question(question)
            sparql_query = gemini_transformer.transform_taln_analysis_to_sparql(taln_analysis)
            method_used = "taln_gemini"
        except Exception as e:
            print(f"TALN+Gemini failed, falling back to direct Gemini: {e}")
            sparql_query = gemini_transformer.transform_question_to_sparql(question)
            method_used = "direct_gemini"
            taln_analysis = None
        
        if not sparql_query:
            return jsonify({"error": "Impossible de générer une requête SPARQL"}), 400
        
        # Execute query
        results = sparql_utils.execute_query(sparql_query)
        
        response = {
            "question": question,
            "sparql_query": sparql_query,
            "results": results,
            "method": method_used
        }
        
        if taln_analysis:
            response["taln_analysis"] = taln_analysis
        
        return jsonify(response)
        
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
    
    # QUESTIONS SUR LES VOLONTAIRES
    elif any(word in question_lower for word in ['volontaire', 'volunteer', 'bénévole', 'benevole']):
        if any(word in question_lower for word in ['actif', 'active', 'très actif']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel .
                FILTER(REGEX(?activityLevel, "actif", "i"))
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            }
            ORDER BY ?label
            """
        
        elif any(word in question_lower for word in ['compétence', 'skill', 'compétences', 'skills', 'domaine']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?experience
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills .
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            }
            ORDER BY ?skills
            """
        
        elif any(word in question_lower for word in ['expérience', 'experience', 'antécédent', 'historique']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?experience ?skills ?activityLevel
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience .
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            }
            ORDER BY ?label
            """
        
        elif any(word in question_lower for word in ['contact', 'téléphone', 'phone', 'numéro']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone .
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
            }
            ORDER BY ?label
            """
        
        else:
            # Requête générale pour les volontaires
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?volunteer ?label ?phone ?skills ?activityLevel ?motivation ?experience
            WHERE {
                ?volunteer a <http://webprotege.stanford.edu/RCXXzqv27uFuX5nYU81XUvw> .
                
                OPTIONAL { ?volunteer rdfs:label ?label . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R8BxRbqkCT2nIQCr5UoVlXD> ?phone . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RBqpxvMVBnwM1Wb6OhzTpHf> ?skills . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/RCHqvY6cUdoI8XfAt441VX0> ?activityLevel . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9PW79FzwQKWuQYdTdYlHzN> ?motivation . }
                OPTIONAL { ?volunteer <http://webprotege.stanford.edu/R9tdW5crNU837y5TemwdNfR> ?experience . }
            }
            ORDER BY ?label
            LIMIT 20
            """
    
    # QUESTIONS SUR LES ASSIGNEMENTS
    elif any(word in question_lower for word in ['assignement', 'assignment', 'assignation', 'affectation']):
        if any(word in question_lower for word in ['approuvé', 'approved', 'validé', 'accepté']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?assignment ?label ?volunteer ?startDate ?status ?rating
            WHERE {
                ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
                ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                FILTER(REGEX(?status, "approuvé", "i"))
                
                OPTIONAL { ?assignment rdfs:label ?label . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
            }
            ORDER BY ?startDate DESC
            """
        
        elif any(word in question_lower for word in ['rejeté', 'rejected', 'refusé', 'non approuvé']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?assignment ?label ?volunteer ?startDate ?status ?rating
            WHERE {
                ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
                ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                FILTER(REGEX(?status, "non approuvé", "i"))
                
                OPTIONAL { ?assignment rdfs:label ?label . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
            }
            ORDER BY ?startDate DESC
            """
        
        elif any(word in question_lower for word in ['note', 'rating', 'évaluation', 'score', 'étoile']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?assignment ?label ?volunteer ?startDate ?status ?rating
            WHERE {
                ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
                ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating .
                
                OPTIONAL { ?assignment rdfs:label ?label . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
            }
            ORDER BY DESC(?rating)
            """
        
        elif any(word in question_lower for word in ['statistique', 'stats', 'résumé', 'bilan']):
            return """
            PREFIX webprotege: <http://webprotege.stanford.edu/>
            
            SELECT 
                (COUNT(?assignment) as ?total)
                (COUNT(?approved) as ?approved_count)
                (COUNT(?rejected) as ?rejected_count)
                (AVG(?rating) as ?average_rating)
            WHERE {
                ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
                
                OPTIONAL { 
                    ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                    FILTER(REGEX(?status, "approuvé", "i"))
                    BIND(?assignment as ?approved)
                }
                OPTIONAL { 
                    ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status .
                    FILTER(REGEX(?status, "non approuvé", "i"))
                    BIND(?assignment as ?rejected)
                }
                OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
            }
            """
        
        else:
            # Requête générale pour les assignements
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
    except Exception as e:
        print(f"❌ Error in hybrid search: {str(e)}")
        return jsonify({"error": f"Erreur dans la recherche hybride: {str(e)}"}), 500
