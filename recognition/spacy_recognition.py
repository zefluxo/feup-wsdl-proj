import spacy
from pprint import pprint
from spacy.training.example import Example

from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from itertools import permutations

class RDFResource:
    def __init__(self, entity, entity_type, name, predicates_objects):
        self.entity = entity
        self.entity_type = entity_type
        self.name = name
        self.predicates_objects = predicates_objects

    def __repr__(self):
        return (
            f"RDFResource(entity={self.entity}, type={self.entity_type}, "
            f"name={self.name}, predicates_objects={self.predicates_objects})"
        )
    
class Entity:
    def __init__(self, text_name, text_location, label):
        self.text_name = text_name 
        self.text_location = text_location # saves the start char number
        self.label = label # Person, Event

        self.resource = None
    
    def __repr__(self):
        return (f"Entity(text_name='{self.text_name}', "
                f"text_location={self.text_location}, "
                f"label='{self.label}', "
                f"resource={self.resource})")

class Person:
    def __init__(self, type, name, birth_date, death_date, description, award, member_of, term_period, military_service, activeYearsStartYear, activeYearsEndYear):
        self.name = name
        self.type = type
        self.birth_date = birth_date
        self.death_date = death_date
        self.description = description
        self.award = award
        self.member_of = member_of
        self.term_period = term_period
        self.military_service = military_service
        self.activeYearsStartYear = activeYearsStartYear
        self.activeYearsEndYear = activeYearsEndYear

    def __repr__(self):
        info = [f"Name: {self.name}"
                f"Date of Birth (DOB): {self.birth_date}"
                f"Date of Death (DOD): {self.death_date}"
                f"Description: {self.description if self.description else 'Unspecified'}"]
        if self.type == 'Politician':
                info.append(f"Term Periods: {self.term_period}",
                            f"Member of: {self.member_of}")
        if self.type == 'Militarian':
                info.append(f"Awards: {self.award}",
                            f"Military Service: {self.military_service}")
        if self.type == 'Royalty':
                info.append(f"Starting year of their reign: {self.activeYearsStartYear}",
                            f"Last year of their reign: {self.activeYearsEndYear if self.activeYearsEndYear else 'Still in power.'}")
        return tuple(info)
    
class Event:
    def __init__(self, type, name, description, date, place, superEvent):
        self.type = type
        self.name = name
        self.description = description
        self.date = date
        self.place = place
        self.superEvent = superEvent
    
    def __repr__(self):
        info = [f"Name: {self.name}"
                f"Date of Birth (DOB): {self.birth_date}"
                f"Date of Death (DOD): {self.death_date}"
                f"Description: {self.description if self.description else 'Unspecified'}"]


# load multilingual spacy model

def run_spacy(text_input, language):

    lang = ''
    match language:
        case "English":
            lang = 'en'
            nlp = spacy.load("en_core_web_trf")
        case "Español":
            lang = 'es'
            nlp = spacy.load("es_core_web_trf")
        case "Português":
            lang = 'pt'
            nlp = spacy.load("pt_core_web_trf")

    input_entities = nlp(text_input)
    entity_list = []    

    # group entities by labels if they are found near each other
    current_entity_text = []
    current_label = None
    current_start = 0
    
    for ent in input_entities.ents:
        print(ent.text, ent.label_)

        # stop if label is not repeated
        if current_label is None or ent.label_ != current_label:

            if current_entity_text:
                # label changed -> save scouted entity
                new_entity = Entity(text_name=" ".join(current_entity_text), text_location=current_start, label=current_label)
                entity_list.append(new_entity)
                
            # else and default start new entity group
            current_start = ent.end_char
            current_label = ent.label_
            current_entity_text = []

        # same label -> append new token to current scouted entity
        current_entity_text.append(ent.text)

    # append the last group
    if current_entity_text:
        new_entity = Entity(text_name=" ".join(current_entity_text), text_location=current_start, label=current_label)
        entity_list.append(new_entity)

    filtered_list = list(filter(lambda entity: entity.label in ["PERSON", "EVENT", "WORK_OF_ART"], entity_list))
    return filtered_list, lang
 
def sparql_to_resource(sparql_object):
    entity = str(sparql_object[0])  # ?entity
    entity_type = str(sparql_object[1])  # ?type
    name = str(sparql_object[2])  # ?name
    predicate = str(sparql_object[3])  # ?predicate
    obj = str(sparql_object[4])  # ?object

    newResource = RDFResource(entity, entity_type, name, [])
    newResource.predicates_objects.append((predicate, obj))
    return newResource
    

def query_for_person(keyword, graph: Graph, language): 
    print(f"Querying for {keyword}")
    query = f"""
            SELECT ?entity ?type ?name ?birthDate ?deathDate ?description ?award ?memberOf ?termPeriod ?militaryService ?activeYearsStartYear ?activeYearsEndYear
            WHERE {{
                ?entity a ?type .
                        ?entity hist:alias ?name .
                        ?entity hist:birthDate ?birthDate .
                        OPTIONAL {{ ?entity hist:deathDate ?deathDate }}
                        OPTIONAL {{ ?entity hist:description ?description }}
                        OPTIONAL {{ ?entity hist:award ?award }}
                        OPTIONAL {{ ?entity hist:memberOf ?memberOf }}
                        OPTIONAL {{ ?entity hist:termPeriod ?termPeriod }}
                        OPTIONAL {{ ?entity hist:militaryService ?militaryService }}
                        OPTIONAL {{ ?entity hist:activeYearsStartYear ?activeYearsStartYear }}
                        OPTIONAL {{ ?entity hist:activeYearsEndYear ?activeYearsEndYear }}
                ?type rdfs:subClassOf* hist:Person .
                FILTER (REGEX(LCASE(?name), "{keyword}", "i"))
                FILTER(LANG(?name) IN ('{language}'))
                
                }}
            """

    results = list(graph.query(query))
    

    return results

def query_for_event(keyword, graph: Graph, language): 
    
    query = f"""
            SELECT ?entity ?type ?name ?predicate ?object
            WHERE {{
                ?entity a ?type ;
                        hist:alias ?name ;

                        ?predicate ?object .

                ?type rdfs:subClassOf* hist:Event .
                FILTER (REGEX(LCASE(?name), "{keyword}", "i"))
                FILTER(LANG(?abstract) IN ('{language}'))
                }}
            """

    results = list(graph.query(query))

    return results



# entity list consists of ["Entity_name", "Entity_label"] entries
def query_knowledge_base(entity_list, graph: Graph, language):


    match language:
        case 'en':
            stop_words = ["the", "is", "in", "and", "of", "to", "a", "with"]
        case 'es':
            stop_words = ["el", "es", "en", "y", "de", "la", "que", "con"]
        case 'pt':
            stop_words = ["o", "é", "em", "e", "de", "a", "que", "com"]

    for entity in entity_list:

        query_results = []
        
        # query based on label
        match entity.label:

            case "PERSON":
                query_results = query_for_person(entity.text_name, graph, language)

                # try to find entity in database through combinations of its full text name
                if len(query_results) == 0:
                    print("\nNo results found for full text.")
                
                    trimmed_name = [word for word in entity.text_name.split() if word.lower() not in stop_words]

                    combinations = []
                    for word in range(1, len(trimmed_name) + 1): 
                        combinations.extend([" ".join(p) for p in permutations(trimmed_name, word)])
                    combinations = sorted(combinations, key=len, reverse=True)

                    i = 0
                    while len(query_results) == 0 and i != len(combinations): 
                        query_results = query_for_person(combinations[i], graph, language)
                        print(f"\nTrying to find {entity.text_name} through {combinations[i]}...")
                        i += 1


            case "EVENT":
                query_results = query_for_event(entity.text_name, graph, language)

                # try to find entity in database through combinations of its full text name
                if len(query_results) == 0:
                
                    trimmed_name = [word for word in entity.text_name.split() if word.lower() not in stop_words]

                    combinations = []
                    for word in range(1, len(trimmed_name) + 1): 
                        combinations.extend([" ".join(p) for p in permutations(trimmed_name, word)])
                    combinations = sorted(combinations, key=len, reverse=True)

                    i = 0
                    while len(query_results) == 0 and i != len(combinations): 
                        query_results = query_for_event(combinations[i], graph, language)
                        print(f"\nTrying to find {entity.text_name} through {combinations[i]}...")
                        i += 1
        
        # parse the retrieved results   
        if len(query_results) == 0:
            print(f"""\n No results found for {entity.text_name} tagged as "{entity.label}". Skipping...""")
            continue
        
        # query_results = query_results[0] # no disambiguation done here - we get the first matching entity 
        print(f"Query results: {query_results}")

        resource = sparql_to_resource(query_results)
        entity.resource = resource
        # pprint(f"object: {entity.resource}")

    return entity_list

    
 

