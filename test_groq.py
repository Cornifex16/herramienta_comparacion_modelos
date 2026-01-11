# Documentacion: https://console.groq.com/docs/overview
from groq import Groq
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

client = Groq(
    # reemplazar con la API_KEY propia o setearla como variable de entorno
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": Template,
        }
    ],
    model="llama-3.3-70b-versatile",
)

respuesta = chat_completion.choices[0].message.content

data = json.loads(respuesta)

with open("respuesta_G.json", "w") as file:
    json.dump(data, file, indent=4)

print(chat_completion.choices[0].message.content)