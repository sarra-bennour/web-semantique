from flask import Blueprint, jsonify, request
from sparql_utils import sparql_utils
import re

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def semantic_search():
    """Recherche sémantique - transformation question en SPARQL"""
    try:
        data = request.json
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

def transform_question_to_sparql_combined(question):
    """Transforme une question en français en requête SPARQL - Version combinée"""
    question_lower = question.lower()
    
    # QUESTIONS SUR LES CAMPAGNES
    if any(word in question_lower for word in ["campagne", "campaign"]):
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

    # QUESTIONS SUR LES ÉVÉNEMENTS (from the first function)
    elif any(word in question_lower for word in ['événement', 'event', 'évènement']):
        if 'où' in question_lower or 'where' in question_lower or 'lieu' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?location ?locationName ?address ?city ?date
            WHERE {
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName ;
                     eco:address ?address .
                OPTIONAL { ?loc eco:city ?city . }
            }
            ORDER BY ?date
            """
        elif 'quand' in question_lower or 'when' in question_lower or 'date' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?date ?locationName
            WHERE {
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc .
                ?loc eco:locationName ?locationName .
            }
            ORDER BY ?date
            """
        elif 'qui organise' in question_lower or 'organisateur' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?organizer ?firstName ?lastName
            WHERE {
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:isOrganizedBy ?organizer .
                ?organizer eco:firstName ?firstName ;
                          eco:lastName ?lastName .
            }
            """
        else:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?event ?title ?description ?date ?locationName ?maxParticipants
            WHERE {
                ?event a eco:Event ;
                       eco:eventTitle ?title ;
                       eco:eventDate ?date ;
                       eco:isLocatedAt ?loc ;
                       eco:maxParticipants ?maxParticipants .
                ?loc eco:locationName ?locationName .
                OPTIONAL { ?event eco:eventDescription ?description . }
            }
            ORDER BY ?date
            """
    
    # QUESTIONS SUR LES LOCATIONS
    elif any(word in question_lower for word in ['location', 'lieu', 'endroit', 'salle', 'place']):
        if 'disponible' in question_lower or 'available' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price
            WHERE {
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity ;
                         eco:price ?price .
                OPTIONAL { ?location eco:city ?city . }
                OPTIONAL { ?location eco:reserved ?reserved . }
                OPTIONAL { ?location eco:inRepair ?inRepair . }
                FILTER (!BOUND(?reserved) || ?reserved = "false")
                FILTER (!BOUND(?inRepair) || ?inRepair = "false")
            }
            ORDER BY ?name
            """
        elif 'paris' in question_lower or 'new york' in question_lower or 'ville' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?country ?capacity ?price
            WHERE {
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity ;
                         eco:price ?price .
                OPTIONAL { ?location eco:city ?city . }
                OPTIONAL { ?location eco:country ?country . }
            }
            ORDER BY ?city ?name
            """
        else:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?location ?name ?address ?city ?capacity ?price
            WHERE {
                ?location a eco:Location ;
                         eco:locationName ?name ;
                         eco:address ?address ;
                         eco:capacity ?capacity ;
                         eco:price ?price .
                OPTIONAL { ?location eco:city ?city . }
            }
            ORDER BY ?name
            """
    
    # QUESTIONS SUR LES ORGANISATEURS ET VOLONTAIRES
    elif any(word in question_lower for word in ['utilisateur', 'user', 'personne', 'organisateur', 'volontaire']):
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
        elif 'volontaire' in question_lower or 'bénévole' in question_lower:
            return """
            PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
            SELECT ?user ?firstName ?lastName ?email ?role
            WHERE {
                ?user a eco:User ;
                      eco:firstName ?firstName ;
                      eco:lastName ?lastName ;
                      eco:email ?email ;
                      eco:role ?role .
                FILTER(REGEX(?role, "volunteer", "i"))
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