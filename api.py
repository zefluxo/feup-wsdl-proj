import requests

excerpt = "Welcome to Significant Others. I'm Liza Powel O'Brien and in our final episode of season two, we are talking about a figure who looms so large. He is both overly invoked and commonly misunderstood. His ideas were so potent. They have been named as the cause of everything from the French socialist revolts and the Russian revolution to political correctness and the January 6th insurrection. Arguably the world as we know it would truly be different without him. He was a massive force in our shared history and yet he was also a human being. He drank and smoked and laughed with his friends. He played games with his kids."
params = {
    "text": excerpt,
    "confidence": 0.5
}
headers = { 'accept': 'application/json' }

result = requests.get(
    url = "https://api.dbpedia-spotlight.org/en/annotate",
    params = params,
    headers = headers
)

data = result.json()

for resource in data['Resources']:
    print(resource)