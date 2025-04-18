from retrieval import populate
from recognition import spacy_recognition

import streamlit as st
import re
import json

g = populate.get_database()

text_input = """Napoleon Bonaparte rose to prominence during the French Revolution.
   He became a key figure in shaping European politics. The Battle of Waterloo marked his ultimate defeat.
   Despite this, his legacy remains influential to this day.""" 

format_dict = {
    
    'birthDate': 'Date of Birth (DOB)',
    'deathDate': 'Date of Death (DOD)',
    'award': 'Awards',
    'memberOf': 'Affiliated Parties',
    'termPeriod': 'Period of served term',
    'militaryService': 'Military time served',
    'activeYearsStartYear': 'First year of their reign',
    'activeYearsEndYear': 'Last year of their reign',
    'superEvent': 'Overarching Event',
    'place': 'Location'
    
}

st.set_page_config(page_title="ChronoLinker", layout="centered")
st.markdown("<h1 style='text-align: center;'>ChronoLinker</h1>", unsafe_allow_html=True)

text_query_tab, sparql_tab = st.tabs(['Entity Recognition', 'SPARQL Query'])

with text_query_tab:

    language = st.selectbox(
        "Choose your language:",
        ["English", "Português", "Español"]
    )

    user_input = st.text_area("Enter your text:", "", height=150)

    if st.button("Submit"):
        if user_input:
            entity_list, lang = spacy_recognition.run_spacy(user_input, language)
            identified_entities = spacy_recognition.query_knowledge_base(entity_list, g, lang)

            final_text = user_input

            css = "<style>"

            if not identified_entities: st.write('No entities found, please check for spelling errors.')
            else:

                dict_entities = {}
                st.write(f"**Found entities:** ")
                for entity in identified_entities:

                    data, my_entity = identified_entities[entity]
                    end = my_entity.text_location
                    text = my_entity.text_name
                    start = end - len(text)

                    pattern = r'\b' + re.escape(text) + r'\b'  # Ensure we match whole words only
                    span_tag = f'<span class="hover-{text.lower().replace(" ","-")}">{text}</span>'
                    css += f""" .hover-{text.lower().replace(' ','-')} {{ color: blue; text-decoration: underline; position: relative; }} 
                                     .hover-{text.lower().replace(' ','-')}:hover::after {{ content: "content-from-{text.lower().replace(' ','-')}";
                                    position: absolute;
                                    background-color: white;
                                    border: 1px solid #ccc;
                                    padding: 5px;
                                    width: 700px;
                                    top: 20px;
                                    left: 0;
                                    z-index: 10; }}"""
                    final_text = re.sub(pattern, span_tag, final_text)
                    dict_entities[text] = ""

                    st.write(f"**{entity}** of type {data['type']}:")
                    for key, value in data.items():
                        if key == 'type' or value == "Unspecified": continue

                        formatted_key = key if key not in format_dict.keys() else format_dict[key]
                        dict_entities[text] += f"""{str(formatted_key).capitalize()}: {data[key]}"""
                        st.write(f"**{str(formatted_key).capitalize()}**: {data[key]}")
                    st.divider()    
                    css += "</style>"
                    for entity in dict_entities.keys():
                        css=css.replace(f"content-from-{entity.lower().replace(' ','-')}", dict_entities[entity])
          
            st.markdown(css, unsafe_allow_html=True)
            st.markdown(final_text, unsafe_allow_html=True)
            st.divider()
        

        else:
            st.write("Please enter some text.")
            
with sparql_tab:
    
    sparql_query = st.text_area("Enter your SPARQL query:", "", height=200)

    if st.button("Submit", key="sparql_submit"):
        if sparql_query.strip():
            try:
                result = populate.run_sparql_query(sparql_query, g)  
                formatted_result = json.dumps(result, indent=2)
                st.json(formatted_result)
            except Exception as e:
                st.error(f"Error executing SPARQL query: {str(e)}")
        else:
            st.write("Please enter a SPARQL query.")


