from retrieval import populate
from recognition import spacy_recognition

import streamlit as st

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
        
        if not identified_entities: st.write('No entities found, please check for spelling errors.')
        else:
            print("PLEASEEEEE")
            st.write(f"**Found entities:** ")
            for entity in identified_entities: 
                data = identified_entities[entity]
                st.write(f"**{entity}** of type **{data['type']}**:")
                for key, value in data.items():
                    if key == 'type': continue

                    formatted_key = key if key not in format_dict.keys() else format_dict[key]
                    st.write(f"**{str(formatted_key).capitalize()}**: {data[key]}")

    else:
        st.write("Please enter some text.")


