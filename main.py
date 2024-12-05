from SPARQLWrapper import SPARQLWrapper, JSON

sparql_driver = SPARQLWrapper(
    "http://dbpedia.org/sparql"
)

sparql_driver.setReturnFormat(JSON)

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

universal_data = ['rdfs:label', 'dbo:abstract', 'dbo:birthDate', 'dbo:deathDate', 'owl:sameAs', '']
specific_data = {
    
    'dbo:Politician': ['dbo:termPeriod'], # objects of class 'time period' which has dbo:start/end has xsd:date
    'dbo:MilitaryPerson': ['dbo:militaryService'], # objects of class 'militaryService' have dbo:serviceStart/EndYear
    'dbo:Philosopher': [],
    'dbo:Scientist': [],
    'dbo:Artist': [],
    'dbo:Writer': [],
    'dbo:Explorer': [],
    'dbo:Royalty': ['dbo:activeYearsStartYear', 'dbo:activeYearsEndYear', ],

}

# retrieve persons

sparql_driver.setQuery("""

PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?entity ?label ?date
WHERE {
  ?entity a dbo:SocietalEvent .
  ?entity rdfs:label ?label .  FILTER(LANG(?label) = "en") .
  ?entity dbp:date ?date .
                       
  FILTER(CONTAINS(LCASE(?label), "anglo-french war")) 
}
                       
LIMIT 10

""")

sparql_driver.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?entity ?label ?abstract ?birthDate ?deathDate ?country ?sameAs
WHERE {
  ?entity a ?type .
  VALUES ?type {
    dbo:Politician
    dbo:MilitaryPerson
    dbo:Philosopher
    dbo:Scientist
    dbo:Artist
    dbo:Writer
    dbo:Explorer
    dbo:Royalty
    dbo:Cleric
    dbo:Athlete
    dbo:Inventor
    dbo:ReligiousPerson
  }
  OPTIONAL { ?entity rdfs:label ?label . FILTER (lang(?label) = "en") }
  OPTIONAL { ?entity rdfs:abstract ?abstract . FILTER (lang(?abstract) = "en") }
  OPTIONAL { ?entity dbo:birthDate ?birthDate . }
  OPTIONAL { ?entity dbo:deathDate ?deathDate . }
  OPTIONAL { ?entity dbo:country ?country . }
}
LIMIT 100
""")


try: 

    result = sparql_driver.queryAndConvert()

    for entity in result['results']['bindings']:
        """ print([
            entity['label']['value'],
            entity['comment']['value'],
            entity['birthDate']['value'],
            entity['deathDate']['value'],
            entity['country']['value']
        ]) """
        print(entity)

except Exception as e: print("uhohhhhh " + str(e.with_traceback_()))

