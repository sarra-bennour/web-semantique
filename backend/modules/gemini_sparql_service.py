import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

class GeminiSPARQLTransformer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        # Utilisez le bon nom de modèle pour votre version d'API
        try:
            self.model = genai.GenerativeModel('models/gemini-pro')
            print("✅ Gemini initialized successfully with models/gemini-pro")
        except Exception as e:
            print(f"❌ Error with models/gemini-pro: {e}")
            # Fallback à l'ancien nom
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini initialized successfully with gemini-pro")
            except Exception as e2:
                print(f"❌ Both model attempts failed: {e2}")
                raise
        
    def transform_question_to_sparql(self, question: str) -> str:
        """Transform natural language question to SPARQL using Gemini ONLY"""
        try:
            prompt = self._build_prompt(question)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1000,
                )
            )
            
            sparql_query = self._extract_sparql_query(response.text)
            return self._validate_and_clean_query(sparql_query)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_query(question)
    
    def _build_prompt(self, question: str) -> str:
        """Build the prompt for Gemini - FOCUS ON DYNAMIC GENERATION"""
        return f"""You are a SPARQL query generator for an ecological events platform. Convert the natural language question to a valid SPARQL query.

ONTOLOGY CONTEXT:
Prefix: eco: <http://www.semanticweb.org/eco-ontology#>

MAIN CLASSES:
- Event, Location, User, Campaign, Resource, Reservation, Certification

EVENT PROPERTIES:
- eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType

LOCATION PROPERTIES:
- locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType

USER PROPERTIES:
- firstName, lastName, email, role, phone, registrationDate

RESERVATION PROPERTIES:
- belongsToUser, confirmedBy, numberOfTickets, reservationStatus, reservationDate

CERTIFICATION PROPERTIES:
- awardedTo, issuedBy, certificateCode, pointsEarned, certificationType

IMPORTANT QUERY PATTERNS:
- For event type questions: Use FILTER with CONTAINS/REGEX on eventTitle, eventDescription, or eventType
- For location type questions: Use FILTER with CONTAINS/REGEX on locationName, locationType, or address
- For date filters: Use FILTER(?date >= NOW()) for future, FILTER(?date < NOW()) for past
- For city filters: FILTER(CONTAINS(LCASE(STR(?city)), "cityname"))
- For text searches: Use FILTER(CONTAINS(LCASE(STR(?field)), "searchterm"))
- For available locations: FILTER(!BOUND(?reserved) || ?reserved = false) && FILTER(!BOUND(?inRepair) || ?inRepair = false)

CRITICAL RULES:
1. Always use PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
2. Use OPTIONAL for properties that might not exist
3. Use ORDER BY when appropriate for sorting
4. Use LIMIT 20-50 to prevent too many results
5. Make location properties OPTIONAL (locationName, city, etc.)
6. Return ONLY the SPARQL query, no explanations
7. Be creative and adapt to the specific question

QUESTION: "{question}"

SPARQL QUERY:"""
    
    def _extract_sparql_query(self, text: str) -> str:
        """Extract clean SPARQL query from Gemini response"""
        # Remove markdown code blocks
        text = re.sub(r'```.*?\n', '', text)
        text = re.sub(r'```', '', text)
        
        # Find the SPARQL query
        lines = text.split('\n')
        query_lines = []
        in_query = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('PREFIX', 'SELECT', 'CONSTRUCT', 'ASK', 'DESCRIBE')):
                in_query = True
            if in_query:
                if stripped and not stripped.startswith('QUESTION:'):
                    query_lines.append(line)
        
        query = '\n'.join(query_lines).strip()
        
        # Ensure PREFIX is included
        if 'PREFIX eco:' not in query:
            query = f"PREFIX eco: <http://www.semanticweb.org/eco-ontology#>\n{query}"
            
        return query
    
    def _validate_and_clean_query(self, query: str) -> str:
        """Validate and clean the SPARQL query"""
        # Basic validation
        if not query or 'SELECT' not in query:
            return self._get_fallback_query("events")
        
        # Ensure location properties are optional
        if '?location eco:locationName ?locationName' in query and 'OPTIONAL' not in query:
            query = query.replace(
                '?location eco:locationName ?locationName .',
                'OPTIONAL { ?location eco:locationName ?locationName . }'
            )
        
        if '?location eco:city ?city' in query and 'OPTIONAL' not in query:
            query = query.replace(
                '?location eco:city ?city .',
                'OPTIONAL { ?location eco:city ?city . }'
            )
        
        # Ensure LIMIT is reasonable
        if 'LIMIT' not in query:
            query += '\nLIMIT 50'
        
        return query
    
    def _get_fallback_query(self, question: str) -> str:
        """Simple fallback for emergency cases only"""
        return """
        PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
        SELECT ?item ?name ?type
        WHERE {
            {
                ?item a eco:Event ;
                     eco:eventTitle ?name .
                BIND("Event" as ?type)
            }
            UNION
            {
                ?item a eco:Location ;
                     eco:locationName ?name .
                BIND("Location" as ?type)
            }
        }
        ORDER BY ?type ?name
        LIMIT 20
        """