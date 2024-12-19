from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from pathlib import Path

from retrieval.people import people
from retrieval.events import events

def get_database():

    dbpedia_driver = SPARQLWrapper( "http://dbpedia.org/sparql" )
    yago_driver = SPARQLWrapper( "https://yago-knowledge.org/sparql/query" )

    dbpedia_driver.setReturnFormat(JSON)
    yago_driver.setReturnFormat(JSON)

    drivers = [dbpedia_driver, yago_driver]

    g = Graph(bind_namespaces="rdflib")

    data = Path('./db.ttl')
    if not data.exists():

        print('Creating knowledge base...')
        g.parse("retrieval/ontology.ttl", format="turtle")

        events.fetch_events(drivers, g)
        people.fetch_people(drivers, g)
        g.serialize("db.ttl")

    else: 
        print('Loading knowledge base...') 
        g.parse('db.ttl')
    
    return g

def run_sparql_query(query, graph: Graph):
    
    results = graph.query(query)
    results_dict = {
        
        str(row['entity']): {str(var): str(row[var]) for var in row.labels if var != 'entity'}
        for row in results
        
    }

    return results_dict
