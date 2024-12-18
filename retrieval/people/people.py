from pprint import pprint
from pathlib import Path
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import XSD, RDF

from utils import date_parser

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

def fetch_people(drivers, graph: Graph):
    
    dbpedia_fetch(drivers[0], graph)
    #yago_fetch(drivers[1], graph)
    
    
def dbpedia_fetch(driver, graph: Graph):
    
    hist = Namespace(graph.namespace_manager.store.namespace('hist'))    
    dbpedia_queries = Path("retrieval/people/dbpedia_queries").iterdir()
    
    for query in dbpedia_queries:
        
        person_type = query.name.split('_')[0].capitalize()
        print(f'[PEOPLE] Fetching {person_type}s from DBPedia...')

        with query.open('r') as file:
            
            driver.setQuery(file.read())
                
            try: 

                result = driver.queryAndConvert()

                for entity in result['results']['bindings']:
                    
                    resource_name = entity['entity']['value'].split('/')[-1].replace("-", "_").replace("–", "_").replace("'","").replace(",","").replace(".","")
                    person = hist[resource_name]
                    person_name = Literal(entity['label']['value'])
                    person_description = Literal(entity['abstract']['value'])
                    birth_date = date_parser.parse(entity['birthDate']['value'])
                    #same_events = [URIRef(same) for same in entity['sameAs']['value'].split(',')]
                        
                    if not birth_date: continue
                    birth_date = Literal(birth_date, datatype=XSD.date)

                    graph.add((person, RDF.type, hist[person_type]))
                    graph.add((person, hist['alias'], person_name))
                    graph.add((person, hist['description'], person_description))
                    graph.add((person, hist['birthDate'], birth_date))
                    
                    if 'deathDate' in entity: 
                        death_date = date_parser.parse(entity['deathDate']['value'])
                        if not death_date: continue
                        death_date = Literal(death_date, datatype=XSD.date)
                        graph.add((person, hist['deathDate'], death_date))
                        
                    add_specific_fields(entity, person, graph, person_type)

                    #for same in same_events: graph.add((event, rdflib.namespace.OWL.sameAs, same))

            except Exception as e: print("[ERROR] " + str(e.with_traceback()))
    

def add_specific_fields(entity, person, graph: Graph, person_type):
    
    dbr = Namespace(graph.namespace_manager.store.namespace('dbr'))
    hist = Namespace(graph.namespace_manager.store.namespace('hist'))
    
    match person_type:
        case "Politician":
            term_period = Literal(entity['termPeriod']['value']) if not entity['termPeriod']['type'] == 'uri' else URIRef(entity['termPeriod']['value'])
            graph.add((person, hist['termPeriod'], term_period))
        case "Militarian":
            military_service = Literal(entity['militaryService']['value']) if not entity['militaryService']['type'] == 'uri' else URIRef(entity['militaryService']['value'])
            graph.add((person, hist['militaryService'], military_service))
        case "Royalty":
            activeYearsStartYear = date_parser.parse(entity['activeYearsStartYear']['value'])
            if activeYearsStartYear:
                activeYearsStartYear = Literal(entity['activeYearsStartYear']['value'], datatype=XSD.gYear)
                graph.add((person, hist['activeYearsStartYear'], activeYearsStartYear))
            if 'activeYearsEndYear' in entity:
                activeYearsEndYear = date_parser.parse(entity['activeYearsEndYear']['value'])
                if activeYearsEndYear:
                    activeYearsEndYear = Literal(entity['activeYearsEndYear']['value'], datatype=XSD.gYear)
                    graph.add((person, hist['activeYearsEndYear'], activeYearsEndYear))
        