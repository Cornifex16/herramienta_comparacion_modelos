import os
import requests
from sambanova import SambaNova
from groq import Groq
from cerebras.cloud.sdk import Cerebras


def llamadaSambaNova(texto, id):
    cliente = SambaNova(
        api_key=os.environ.get("SAMBANOVA_API_KEY"),
        base_url="https://api.sambanova.ai/v1",
    )

    data = cliente.chat.completions.create(
        model="Meta-Llama-3.3-70B-Instruct",
        messages=[
            {
                "role": "user",
                "content": texto
            }
        ],
    )

    respuesta = {
                    "data_id": id,
                    "model": data.model,
                    "resultado": data.choices[0].message.content,
                    "usage": data.usage.model_dump(),
                    "res_id": data.id
                }
    
    return respuesta

def llamadaGroq(texto, id):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    data = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": texto
            }
        ],
        model="llama-3.3-70b-versatile"
    )
    respuesta = {
                    "data_id": id,
                    "model": data.model,
                    "resultado": data.choices[0].message.content,
                    "usage": data.usage.model_dump(),
                    "res_id": data.id
                }
    
    return respuesta

def llamadaOpenRouter(texto, id, modelo, temperature, max_tokens):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "system",
                "content": "You are a topic generator."
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    respuesta = {
                    "data_id": id,
                    "model": data.get("model"),
                    "resultado": data.get("choices", [{}])[0].get("message", {}).get("content"),
                    "usage": data.get("usage"),
                    "res_id": data.get("id")
                }
    
    return respuesta

def llamadaCerebras(texto, id):
    cliente = Cerebras(
        api_key=os.environ.get("CEREBRAS_API_KEY")
    )
    data = cliente.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": texto
            }
        ],
        model="llama-3.3-70b"
    )
    respuesta = {
                    "data_id": id,
                    "model": data.model,
                    "resultado": data.choices[0].message.content,
                    "usage": data.usage.model_dump(),
                    "res_id": data.id
                }
    
    return respuesta

def tester(modelo):
    print(modelo("escribe hola mundo", "1"))

if __name__ == "__main__":
    tester(llamadaSambaNova)