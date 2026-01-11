# Documentacion: https://openrouter.ai/docs/quickstart
import requests
import json
import os

documento = "Medicare Prescription Drug Price Negotiation Act of 2007 - Amends title XVIII (Medicare) of the Social Security Act to require the Secretary of Health and Human Services to negotiate with pharmaceutical manufacturers the prices that may be charged to prescription drug plan sponsors and Medicare Advantage organizations for covered part D drugs for part D eligible individuals enrolled under a prescription drug plan or under a Medicare Advantage prescription drug (MA-PD) plan."

Template = f"""Given the following document, your task is to
generate a topic word for the article, followed by
a short description of the meaning of the topic
given by you. Your response should follow the
JSON format, with the first key being
'topic_word', the second key being 'description'.
The value corresponding to the first key is the
topic word, and the value corresponding to the
second key is the description of the topic. The
description should be no more than two sentences.
Return only the JSON data without any
explanation.
[Instructions]
- The topic should be a single word or a short
phrase of 2-3 words.
[Document] {documento}
[Your response]"""

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    # reemplazar con la API_KEY propia o setearla como variable de entorno
    "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
    "Content-Type": "application/json"
}
payload = {
"model": "meta-llama/llama-3.3-70b-instruct:free",
"messages": [
{
"role": "user",
"content": Template
}
]
}

response = requests.post(url, headers=headers, json=payload)

respuesta = response.json()

print(respuesta)

respuesta_pros = response.json()["choices"][0]["message"]["content"]

# un problema es que puede generar una respuesta que no esta en el formato adecuado usando variado numero de ' en vez de una
# posible solucion seria crear una forma de reformatear el texto o repetir el proceso de nuevo hasta obtener el resultado deseado
data = json.loads(respuesta_pros)

with open('respuesta_OP.json', 'w') as file:
    json.dump(data, file, indent=4)

print(respuesta_pros)