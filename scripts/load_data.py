from rdflib import Graph
import requests
import os

# Configuration Fuseki
FUSEKI_ENDPOINT = "http://localhost:3030/eco-ontology"
FUSEKI_DATA = f"{FUSEKI_ENDPOINT}/data"
FUSEKI_UPDATE = f"{FUSEKI_ENDPOINT}/update"

def load_ontology_to_fuseki():
    try:
        # Charger l'ontologie en ignorant les erreurs de date
        g = Graph()
        print("Chargement du fichier RDF...")
        
        # Parser en ignorant les erreurs
        g.parse("../data/eco-ontology.rdf", format="xml", errors='ignore')
        print(f"Ontologie chargée: {len(g)} triplets trouvés")
        
        # Upload vers Fuseki par lots de triplets
        print("Upload des données vers Fuseki...")
        
        # Méthode 1: Utiliser SPARQL INSERT pour chaque triplet
        success_count = 0
        error_count = 0
        
        for triple in g:
            try:
                subject = triple[0].n3()
                predicate = triple[1].n3()
                obj = triple[2].n3()
                
                # Créer la requête INSERT
                insert_query = f"""
                INSERT DATA {{
                    {subject} {predicate} {obj} .
                }}
                """
                
                headers = {
                    'Content-Type': 'application/sparql-update'
                }
                
                response = requests.post(FUSEKI_UPDATE, data=insert_query, headers=headers)
                
                if response.status_code in [200, 204]:
                    success_count += 1
                else:
                    error_count += 1
                    print(f"Erreur avec le triplet: {triple}")
                    
            except Exception as e:
                error_count += 1
                continue
        
        print(f"✅ Upload terminé: {success_count} triplets chargés, {error_count} erreurs")
        
        # Vérifier que les données sont bien chargées
        test_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{FUSEKI_ENDPOINT}/query", params={'query': test_query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            count = data['results']['bindings'][0]['count']['value']
            print(f"📊 Total des triplets dans Fuseki: {count}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

def clear_dataset():
    """Vider le dataset avant de charger les nouvelles données"""
    try:
        clear_query = "CLEAR ALL"
        
        headers = {
            'Content-Type': 'application/sparql-update'
        }
        
        response = requests.post(FUSEKI_UPDATE, data=clear_query, headers=headers)
        
        if response.status_code in [200, 204]:
            print("✅ Dataset vidé avec succès")
        else:
            print(f"⚠️ Impossible de vider le dataset: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Erreur lors du vidage: {str(e)}")

def test_fuseki_connection():
    """Tester la connexion à Fuseki"""
    try:
        response = requests.get(FUSEKI_ENDPOINT)
        if response.status_code == 200:
            print("✅ Connexion à Fuseki réussie")
            return True
        else:
            print(f"❌ Fuseki ne répond pas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Impossible de se connecter à Fuseki: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Début du chargement des données...")
    
    if test_fuseki_connection():
        clear_dataset()
        load_ontology_to_fuseki()
    else:
        print("❌ Veuillez démarrer Fuseki d'abord: ./fuseki-server")