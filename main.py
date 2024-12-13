from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, BNode, Literal
import rdflib.namespace

dbpedia_driver = SPARQLWrapper( "http://dbpedia.org/sparql" )
dbpedia_driver.setReturnFormat(JSON)

yago_driver = SPARQLWrapper( "https://yago-knowledge.org/sparql/query" )
yago_driver.setReturnFormat(JSON)

""" # Temporal Properties
dbo:birthDate a rdf:Property ;
    rdfs:domain dbo:Person ;
    rdfs:range xsd:dateTime .

dbo:deathDate a rdf:Property ;
    rdfs:domain dbo:Person ;
    rdfs:range xsd:dateTime .

dbo:rulingPeriod a rdf:Property ;
    rdfs:domain dbo:Person ;
    rdfs:range dbo:TimeSpan .

dbo:startDate a rdf:Property ;
    rdfs:domain dbo:Event ;
    rdfs:range xsd:dateTime .

dbo:endDate a rdf:Property ;
    rdfs:domain dbo:Event ;
    rdfs:range xsd:dateTime . """

universal_data = ['rdfs:label', 'dbo:abstract', 'dbo:birthDate', 'dbo:deathDate', 'owl:sameAs']
specific_data = {
    
    'dbo:Politician': ['dbo:termPeriod'], # objects of class 'time period' which has dbo:start/end has xsd:date
    'dbo:MilitaryPerson': ['dbo:militaryService'], # objects of class 'militaryService' have dbo:serviceStart/EndYear
    'dbo:Philosopher': [],
    'dbo:Scientist': [],
    'dbo:Artist': [],
    'dbo:Writer': [],
    'dbo:Explorer': [],
    'dbo:Royalty': ['dbo:activeYearsStartYear', 'dbo:activeYearsEndYear']

}

# retrieve persons

dbpedia_driver.setQuery("""

PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?entity ?label ?date ?abstract GROUP_CONCAT(DISTINCT ?sameAs; SEPARATOR = ",") AS ?sameAs
WHERE {
  ?entity a dbo:SocietalEvent .
  ?entity rdfs:label ?label .
  ?entity dbp:date ?date .
  ?entity dbo:abstract ?abstract .
  ?entity owl:sameAs ?sameAs .
                       
  FILTER(LANG(?abstract) IN ('en', 'es', 'pt'))
  FILTER(CONTAINS(LCASE(?label), "anglo-french war")) 
}
                       
""")

g = Graph(bind_namespaces="rdflib")

dbo = Namespace("http://dbpedia.org/ontology/")
dbp = Namespace("http://dbpedia.org/property/")
dbr = Namespace("http://dbpedia.org/resource/")
yago = Namespace("http://yago-knowledge.org/resource/")

g.bind("dbo", dbo)
g.bind("dbp", dbp)
g.bind("dbr", dbr)
g.bind("yago", yago)

try: 

    result = dbpedia_driver.queryAndConvert()

    for entity in result['results']['bindings']:
        
        resource_name = entity['entity']['value'].split('/')[-1].replace("-", "_").replace("–", "_")
        event = dbr[resource_name]
        event_name = Literal(entity['label']['value'])
        event_date = Literal(entity['date']['value'])
        event_description = Literal(entity['abstract']['value'])
        same_events = [URIRef(same) for same in entity['sameAs']['value'].split(',')]
        relevant_events = []

        g.add((event, rdflib.namespace.RDF.type, dbo['SocietalEvent']))
        g.add((event, rdflib.namespace.RDFS.label, event_name))
        g.add((event, dbo.abstract, event_description))
        g.add((event, dbp.date, event_date))
        
        for same in same_events:
            g.add((event, rdflib.namespace.OWL.sameAs, same))

except Exception as e: print("[ERROR] " + str(e.with_traceback_()))

g.serialize("new_ontology.ttl")