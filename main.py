from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from pathlib import Path

from retrieval.people import people
from retrieval.events import events
from recognition import spacy_recognition

import streamlit as st

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
    

# text_input = """Napoleon Bonaparte rose to prominence during the French Revolution.
#    He became a key figure in shaping European politics. The Battle of Waterloo marked his ultimate defeat.
#    Despite this, his legacy remains influential to this day.""" 

st.set_page_config(page_title="Basic Webpage", layout="centered")

# Center the content
st.markdown("<h1 style='text-align: center;'>ChronoLinker</h1>", unsafe_allow_html=True)

language = st.selectbox(
    "Choose your language:",
    ["English", "Português", "Español"]
)

user_input = st.text_area("Enter your text:", "", height=150)

if st.button("Submit"):
    if user_input:
        entity_list, lang = spacy_recognition.run_spacy(user_input, language)
        identified_entities = spacy_recognition.query_knowledge_base(entity_list, g, lang)
        st.write("Found entities: ")
        for entity in identified_entities: st.write(str(entity))
    else:
        st.write("Please enter some text.")

