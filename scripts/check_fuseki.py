from backend.sparql_utils import sparql_utils

def check_count():
    q = '''PREFIX : <http://www.semanticweb.org/eco-ontology#>
SELECT (COUNT(?s) as ?count) WHERE { ?s a :Blog }'''
    res = sparql_utils.execute_query(q)
    print('COUNT RESULT:')
    print(res)

def search_title(term):
    q = f'''PREFIX : <http://www.semanticweb.org/eco-ontology#>
SELECT ?s ?title WHERE {{ ?s a :Blog; :blogTitle ?title . FILTER(CONTAINS(LCASE(STR(?title)),"{term}")) }} LIMIT 10'''
    res = sparql_utils.execute_query(q)
    print(f'SEARCH TERM: {term}')
    print(res)

if __name__ == '__main__':
    check_count()
    search_title('urban composting')
    search_title('compost')
