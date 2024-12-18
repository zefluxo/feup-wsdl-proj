from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from pathlib import Path

from retrieval.people import people
from retrieval.events import events

dbpedia_driver = SPARQLWrapper( "http://dbpedia.org/sparql" )
yago_driver = SPARQLWrapper( "https://yago-knowledge.org/sparql/query" )

dbpedia_driver.setReturnFormat(JSON)
yago_driver.setReturnFormat(JSON)

drivers = [dbpedia_driver, yago_driver]

g = Graph()

data = Path('./db.ttl')
if not data.exists():
    
    g.parse("retrieval/ontology.ttl", format="turtle")
    
    #events.fetch_events(drivers, g)
    people.fetch_people(drivers, g)
    g.serialize("db.ttl")

else: g.parse('db.ttl')
