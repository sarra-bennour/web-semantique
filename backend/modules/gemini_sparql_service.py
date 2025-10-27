import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from typing import Dict, Any

load_dotenv()

class GeminiSPARQLTransformer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        

        try:
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')
            print("Gemini initialized successfully with models/gemini-2.0-flash")
        except Exception as e:
            print(f"Error with models/gemini-2.0-flash: {e}")
            # Fallback to other models
            try:
                self.model = genai.GenerativeModel('models/gemini-flash-latest')
                print("Gemini initialized successfully with models/gemini-flash-latest")
            except Exception as e2:
                print(f"Error with models/gemini-flash-latest: {e2}")
                try:
                    self.model = genai.GenerativeModel('models/gemini-pro-latest')
                    print("Gemini initialized successfully with models/gemini-pro-latest")
                except Exception as e3:
                    print(f"All model attempts failed: {e3}")
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
    
    def transform_taln_analysis_to_sparql(self, taln_analysis: Dict[str, Any]) -> str:
        """
        Transform TALN analysis result to SPARQL using Gemini.
        This is the new method that works with TALN extracted data.
        
        Args:
            taln_analysis: Dictionary containing TALN analysis results
            
        Returns:
            Generated SPARQL query string
        """
        try:
            print(f"DEBUG: Starting Gemini SPARQL generation")
            print(f"DEBUG: TALN Analysis keys: {list(taln_analysis.keys())}")
            print(f"DEBUG: Entities detected: {len(taln_analysis.get('entities', []))}")
            print(f"DEBUG: Intent: {taln_analysis.get('intent', {}).get('primary_intent', 'unknown')}")
            
            prompt = self._build_taln_prompt(taln_analysis)
            print(f"DEBUG: Prompt length: {len(prompt)} characters")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1200,
                )
            )
            
            print(f"DEBUG: Gemini response received: {len(response.text)} characters")
            sparql_query = self._extract_sparql_query(response.text)
            print(f"DEBUG: Extracted SPARQL query: {len(sparql_query)} characters")
            print(f"DEBUG: Query preview: {sparql_query[:200]}...")
            
            validated_query = self._validate_and_clean_query(sparql_query)
            print(f"DEBUG: Final validated query: {len(validated_query)} characters")
            
            return validated_query
            
        except Exception as e:
            print(f"ERROR: Gemini API error with TALN analysis: {e}")
            print(f"DEBUG: Falling back to original question method")
            # Fallback to original question if available
            original_question = taln_analysis.get('original_question', '')
            if original_question:
                return self.transform_question_to_sparql(original_question)
            return self._get_fallback_query("events")
    
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
    
    def _build_taln_prompt(self, taln_analysis: Dict[str, Any]) -> str:
        """
        Build the prompt for Gemini using TALN analysis results.
        This provides much more structured and accurate information to Gemini.
        """
        original_question = taln_analysis.get('original_question', '')
        entities = taln_analysis.get('entities', [])
        intent = taln_analysis.get('intent', {})
        temporal_info = taln_analysis.get('temporal_info', {})
        location_info = taln_analysis.get('location_info', {})
        keywords = taln_analysis.get('keywords', [])
        relationships = taln_analysis.get('relationships', [])
        
        # Build entity context
        entity_context = ""
        if entities:
            entity_list = []
            for entity in entities:
                entity_list.append(f"- {entity['text']} ({entity['ontology_class']})")
            entity_context = f"ENTITIES DETECTED:\n" + "\n".join(entity_list)
        
        # Build intent context
        intent_context = ""
        if intent:
            primary_intent = intent.get('primary_intent', 'unknown')
            query_type = intent.get('query_type', 'general')
            intent_context = f"USER INTENT: {primary_intent} (Query Type: {query_type})"
        
        # Build temporal context
        temporal_context = ""
        if temporal_info.get('relative_time'):
            temporal_context = f"TEMPORAL INFO: {temporal_info['relative_time']}"
            if temporal_info.get('time_expressions'):
                temporal_context += f" (Expressions: {', '.join(temporal_info['time_expressions'])})"
        
        # Build location context
        location_context = ""
        if location_info.get('locations'):
            locations = location_info['locations']
            location_context = f"LOCATIONS MENTIONED: {', '.join(locations)}"
        
        # Build keyword context
        keyword_context = ""
        if keywords:
            keyword_texts = [kw['text'] for kw in keywords[:10]]  # Limit to 10 most important
            keyword_context = f"IMPORTANT KEYWORDS: {', '.join(keyword_texts)}"
        
        # Build relationship context
        relationship_context = ""
        if relationships:
            rel_texts = []
            for rel in relationships:
                rel_texts.append(f"{rel['subject']} -> {rel['predicate']} -> {rel['object']}")
            relationship_context = f"RELATIONSHIPS: {'; '.join(rel_texts)}"
        
        return f"""You are an expert SPARQL query generator for an ecological events platform. Generate a precise SPARQL query based on the structured analysis provided below.

ONTOLOGY CONTEXT:
PREFIX eco: <http://www.semanticweb.org/eco-ontology#>
PREFIX webprotege: <http://webprotege.stanford.edu/>

MAIN CLASSES AND THEIR PROPERTIES:
- Event (eco:Event): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- EducationalEvent (eco:EducationalEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- EntertainmentEvent (eco:EntertainmentEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- CompetitiveEvent (eco:CompetitiveEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- SocializationEvent (eco:SocializationEvent): eventTitle, eventDate, eventDescription, maxParticipants, isLocatedAt, isOrganizedBy, eventStatus, duration, eventImages, eventType
- Location (eco:Location): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Indoor (eco:Indoor): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Outdoor (eco:Outdoor): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- VirtualPlatform (eco:VirtualPlatform): locationName, address, city, country, capacity, price, reserved, inRepair, locationDescription, latitude, longitude, locationImages, locationType
- Campaign (eco:Campaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- AwarenessCampaign (eco:AwarenessCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- CleanupCampaign (eco:CleanupCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- FundingCampaign (eco:FundingCampaign): campaignName, campaignDescription, campaignStatus, startDate, endDate, goal, targetAmount, fundsRaised
- Resource (eco:Resource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- DigitalResource (eco:DigitalResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- EquipmentResource (eco:EquipmentResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- HumanResource (eco:HumanResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- MaterialResource (eco:MaterialResource): resourceName, resourceDescription, resourceCategory, quantityAvailable, unitCost, resourceType
- Volunteer (webprotege:RCXXzqv27uFuX5nYU81XUvw): phone (webprotege:R8BxRbqkCT2nIQCr5UoVlXD), healthIssues (webprotege:R9F95BAS8WtbTv8ZGBaPe42), motivation (webprotege:R9PW79FzwQKWuQYdTdYlHzN), experience (webprotege:R9tdW5crNU837y5TemwdNfR), skills (webprotege:RBqpxvMVBnwM1Wb6OhzTpHf)
- Assignment (webprotege:Rj2A7xNWLfpNcbE4HJMKqN): startDate (webprotege:RD3Wor03BEPInfzUaMNVPC7), status (webprotege:RDT3XEARggTy1BIBKDXXrmx), rating (webprotege:RRatingAssignment)
- Certification (eco:Certification): certificateCode, pointsEarned, certificationType, awardedTo, issuedBy
- Reservation (eco:Reservation): seatNumber, status, belongsToUser, confirmedBy, numberOfTickets, reservationDate
- Blog (eco:Blog): blogTitle, blogContent, category, publicationDate

ANALYSIS RESULTS:
Original Question: "{original_question}"

{entity_context}

{intent_context}

{temporal_context}

{location_context}

{keyword_context}

{relationship_context}

QUERY GENERATION RULES:
1. Always use PREFIX eco: <http://www.semanticweb.org/eco-ontology#> and PREFIX webprotege: <http://webprotege.stanford.edu/>
2. Use webprotege: classes for main entities (webprotege:Event, webprotege:Location, etc.)
3. Use eco: properties for entity attributes (eco:eventTitle, eco:locationName, etc.)
4. CRITICAL: Always use proper SPARQL syntax: ?entity eco:property ?variable
5. Use OPTIONAL for properties that might not exist
6. Use FILTER with CONTAINS/REGEX for text searches
7. Use FILTER with date comparisons for temporal queries
8. Use FILTER with city/location matching for location queries
9. Use ORDER BY when appropriate for sorting
10. Use LIMIT 20-50 to prevent too many results
11. Use GROUP BY and COUNT for counting queries
12. Use UNION for multiple entity types
13. Make location properties OPTIONAL (locationName, city, etc.)
14. Return ONLY the SPARQL query, no explanations
15. Be precise based on the detected entities and intent

SPARQL SYNTAX EXAMPLES:
- Correct: ?event a eco:Event . ?event eco:eventTitle ?title .
- Correct: ?event a eco:EducationalEvent . ?event eco:eventTitle ?title .
- Correct: ?campaign a eco:Campaign . ?campaign eco:campaignName ?name .
- Correct: ?volunteer a webprotege:RCXXzqv27uFuX5nYU81XUvw . ?volunteer webprotege:R8BxRbqkCT2nIQCr5UoVlXD ?phone .
- Correct: ?assignment a webprotege:Rj2A7xNWLfpNcbE4HJMKqN . ?assignment webprotege:RDT3XEARggTy1BIBKDXXrmx ?status .
- Incorrect: eco:eventTitle ?title (missing subject)
- Incorrect: ?event eco:eventTitle (missing object)

IMPORTANT: For events, use UNION to include all event types:
{{
  ?event a eco:Event .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:EducationalEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:EntertainmentEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:CompetitiveEvent .
  ?event eco:eventTitle ?title .
}}
UNION
{{
  ?event a eco:SocializationEvent .
  ?event eco:eventTitle ?title .
}}

Generate a SPARQL query that accurately addresses the user's intent using the detected entities and relationships:

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
        
        # Fix common SPARQL syntax errors
        lines = query.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('PREFIX') or line.startswith('SELECT') or line.startswith('WHERE') or line.startswith('LIMIT') or line.startswith('ORDER'):
                fixed_lines.append(line)
                continue
            
            # Fix missing subject in property statements
            if line.startswith('eco:') and not line.startswith('eco: '):
                # This is a property without a subject, skip it
                print(f"DEBUG: Skipping malformed line: {line}")
                continue
            
            # Fix incomplete triple patterns
            if line.endswith('eco:') and not line.endswith('eco: .'):
                # This is an incomplete triple, skip it
                print(f"DEBUG: Skipping incomplete triple: {line}")
                continue
            
            fixed_lines.append(line)
        
        query = '\n'.join(fixed_lines)
        
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
        PREFIX webprotege: <http://webprotege.stanford.edu/>
        SELECT ?item ?name ?type
        WHERE {
            {
                ?item a eco:Event ;
                     eco:eventTitle ?name .
                BIND("Event" as ?type)
            }
            UNION
            {
                ?item a eco:EducationalEvent ;
                     eco:eventTitle ?name .
                BIND("EducationalEvent" as ?type)
            }
            UNION
            {
                ?item a eco:EntertainmentEvent ;
                     eco:eventTitle ?name .
                BIND("EntertainmentEvent" as ?type)
            }
            UNION
            {
                ?item a eco:CompetitiveEvent ;
                     eco:eventTitle ?name .
                BIND("CompetitiveEvent" as ?type)
            }
            UNION
            {
                ?item a eco:Location ;
                     eco:locationName ?name .
                BIND("Location" as ?type)
            }
            UNION
            {
                ?item a webprotege:RCXXzqv27uFuX5nYU81XUvw ;
                     rdfs:label ?name .
                BIND("Volunteer" as ?type)
            }
            UNION
            {
                ?item a webprotege:Rj2A7xNWLfpNcbE4HJMKqN ;
                     rdfs:label ?name .
                BIND("Assignment" as ?type)
            }
            UNION
            {
                ?item a eco:Campaign ;
                     eco:campaignName ?name .
                BIND("Campaign" as ?type)
            }
        }
        ORDER BY ?type ?name
        LIMIT 20
        """