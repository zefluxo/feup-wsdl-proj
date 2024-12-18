import spacy
from pprint import pprint
from spacy.training.example import Example

from rdflib import Graph
import rdflib.term
from rdflib.plugins.sparql import prepareQuery

from itertools import permutations

# Entity_keywords: ["napoleon", "bonaparte" , "napoleon bonaparte"], Label: Person
# na search
# -> search(napoleon), search(bonaparte), search(napoleon bonaparte)
# nos resultados de cada, soma o número de vezes que apanhas o mesmo URI

# dict: 

## Input Entity -> "Text_Name", "Text_Location (initial_char_number, final_char_number)" "Keywords", "URI"

class Entity:
    def __init__(self, text_name, text_location, label):
        self.text_name = text_name 
        self.text_location = text_location # saves the start char number
        self.label = label # Person, Event

        self.uri = None

# Load the multilingual model

def run_spacy(text_input, language):

    match language:
        case "english":
            nlp = spacy.load("en_core_web_trf")
        case "spanish":
            nlp = spacy.load("es_core_web_trf")
        case "portuguese":
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

    print(vars(entity_list[0]))

    filtered_list = list(filter(lambda entity: entity.label in ["PERSON", "EVENT", "WORK_OF_ART"], entity_list))
    return filtered_list
 


# entity list consists of ["Entity_name", "Entity_label"] entries
def query_knowledge_base(entity_list, graph: Graph):
    
    stop_words = {"of", "the"} 
    
    entities_found = []

    query = ""
    for entity in entity_list:
        
        # try to find entity in database through combinations of its full text name
        trimmed_name = [word for word in entity.text_name.split() if word.lower() not in stop_words]

        combinations = []
        for word in range(1, len(trimmed_name) + 1): 
            combinations.extend([" ".join(p) for p in permutations(trimmed_name, word)])
        
        # query based on label
        match entity.label:

            case "PERSON":
                query = f"""
                        SELECT ?entity ?type ?name ?predicate ?object
                        WHERE {{
                            ?entity a ?type ;
                                    hist:alias ?name ;
                                    ?predicate ?object .

                            ?type rdfs:subClassOf* hist:Person .
                            FILTER (
                                REGEX(LCASE(?name), "{entity.text_name}", "i") ||
                        """

                # Add OR conditions for combinations
                if combinations:
                            query += " || ".join([f'REGEX(LCASE(?name), "{combination}", "i")' for combination in combinations])

                # Close the FILTER clause and WHERE block
                query += """
                    )
                }
                """


            case "EVENT":
                query = f"""
                        SELECT ?entity ?type ?name ?predicate ?object
                        WHERE {{
                            ?entity a ?type ;
                                    hist:alias ?name ;
                                    ?predicate ?object .

                            ?type rdfs:subClassOf* hist:Event .
                            FILTER (
                                REGEX(LCASE(?name), "{entity.text_name}", "i") ||
                        """

                # Add OR conditions for combinations
                if combinations:
                            query += " || ".join([f'REGEX(LCASE(?name), "{combination}", "i")' for combination in combinations])

                # Close the FILTER clause and WHERE block
                query += """
                    )
                }
                """

        
        current_result = graph.query(query)

        current_result_python = []
        for row in current_result:
            print("here")
            result_row = []
            for value in row:
                if isinstance(value, rdflib.term.Literal):
                    result_row.append(value.toPython())  # convert to a Python native type
                else:
                    result_row.append(str(value))  # URIRef or other terms to string

            current_result_python.append(result_row)
            pprint(result_row)
        
        entities_found.append(current_result_python)
        
    
#text_input = """Napoleon Bonaparte rose to prominence during the French Revolution.
#    He became a key figure in shaping European politics. The Battle of Waterloo marked his ultimate defeat.
#    Despite this, his legacy remains influential to this day.""" 

#input= run_spacy(text_input, language="english")
 

