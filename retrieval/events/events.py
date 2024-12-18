from pprint import pprint
from pathlib import Path
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import XSD, RDF

from utils import date_parser

def fetch_events(drivers, graph: Graph):
    print('')
    dbpedia_fetch(drivers[0], graph)
    yago_fetch(drivers[1], graph)
    print('')

def dbpedia_fetch(driver, graph: Graph):
    
    hist = Namespace(graph.namespace_manager.store.namespace('hist'))   
    dbpedia_queries = Path("retrieval/events/dbpedia_queries").iterdir()
    
    for query in dbpedia_queries:
        
        event_type = query.name.split('_')[0].capitalize()
        print(f'[EVENTS] Fetching {event_type}s from DBPedia...')

        with query.open('r') as file:
            
            driver.setQuery(file.read())
                
            try: 

                result = driver.queryAndConvert()

                for entity in result['results']['bindings']:
                    
                    resource_name = entity['entity']['value'].split('/')[-1].replace("-", "_").replace("–", "_").replace("'","")
                    event = hist[resource_name]
                    event_name = Literal(entity['label']['value'], lang = entity['label']['xml:lang'])
                    event_date = date_parser.parse(entity['date']['value'])
                    event_description = Literal(entity['abstract']['value'], lang = entity['abstract']['xml:lang'])
                    event_place = Literal(entity['place']['value']) if not entity['place']['type'] == 'uri' else URIRef(entity['place']['value'])
                    #same_events = [URIRef(same) for same in entity['sameAs']['value'].split(',')]

                    if not event_date: continue
                    event_date = Literal(event_date, datatype=XSD.date)

                    graph.add((event, RDF.type, hist[event_type]))
                    graph.add((event, hist['alias'], event_name))
                    graph.add((event, hist['description'], event_description))
                    graph.add((event, hist['date'], event_date))
                    graph.add((event, hist['place'], event_place))

                    #for same in same_events: graph.add((event, rdflib.namespace.OWL.sameAs, same))

            except Exception as e: print(f'[ERROR] {str(e.with_traceback())}')
    

def yago_fetch(driver, graph: Graph):
    
    hist = Namespace(graph.namespace_manager.store.namespace('hist'))
    yago_queries = Path("retrieval/events/yago_queries").iterdir()
    
    for query in yago_queries:
        
        event_type = query.name.split('_')[0].capitalize()        
        print(f'[EVENTS] Fetching {event_type}s from Yago...')

        with query.open('r') as file:
            
            driver.setQuery(file.read())
            
            try:
                
                result = driver.queryAndConvert()
                
                for entity in result['results']['bindings']:
                    
                    
                    resource_name = entity['entity']['value'].split('/')[-1]
                    event = hist[resource_name]
                    event_name = Literal(entity['label']['value'], lang = entity['label']['xml:lang'])
                    event_place = Literal(entity['location']['value'], lang = entity['location']['xml:lang']) if not entity['location']['type'] == 'uri' else URIRef(entity['location']['value'])
                    
                    graph.add((event, RDF.type, hist[event_type]))
                    graph.add((event, hist['alias'], event_name))
                    graph.add((event, hist['place'], event_place))
                    
                    if 'superEvent' in entity:
                        super_event = Literal(entity['superEvent']['value'], lang = entity['superEvent']['xml:lang']) if not entity['superEvent']['type'] == 'uri' else hist[entity['superEvent']['value'].split('/')[-1]]
                        graph.add((event, hist['superEvent'], super_event))
                
            except Exception as e: print(f'[ERROR] {str(e.with_traceback())}')
            
    return 0