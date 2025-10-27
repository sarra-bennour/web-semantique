#!/usr/bin/env python3
"""
Test simple pour les assignements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.sparql_utils import sparql_utils

def test_assignments():
    """Test de récupération des assignements"""
    print("=== Test Assignements ===")
    
    # Test simple d'abord
    simple_query = """
    SELECT ?assignment WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
    }
    LIMIT 10
    """
    
    print("1. Test simple - compter les assignements:")
    try:
        results = sparql_utils.execute_query(simple_query)
        print(f"✅ Nombre d'assignements trouvés: {len(results)}")
        for i, r in enumerate(results):
            print(f"   {i+1}. {r['assignment']}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test complet
    full_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?assignment ?label ?volunteer ?startDate ?status ?rating
    WHERE {
        ?assignment a <http://webprotege.stanford.edu/Rj2A7xNWLfpNcbE4HJMKqN> .
        
        OPTIONAL { ?assignment rdfs:label ?label . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RBNk0vvVsRh8FjaWPGT0XCO> ?volunteer . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RD3Wor03BEPInfzUaMNVPC7> ?startDate . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RDT3XEARggTy1BIBKDXXrmx> ?status . }
        OPTIONAL { ?assignment <http://webprotege.stanford.edu/RRatingAssignment> ?rating . }
    }
    ORDER BY ?assignment
    """
    
    print("\n2. Test complet avec propriétés:")
    try:
        results = sparql_utils.execute_query(full_query)
        print(f"✅ Nombre d'assignements avec propriétés: {len(results)}")
        
        for i, assignment in enumerate(results[:3]):  # Afficher les 3 premiers
            print(f"\n📋 Assignement {i+1}:")
            for key, value in assignment.items():
                if value:
                    print(f"  - {key}: {value}")
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_assignments()

