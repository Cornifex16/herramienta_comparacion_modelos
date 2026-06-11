import asyncio
import aiohttp
import json
import aiofiles
import os
import requests
import datasets
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


def verificar_nuevo(prompt):
    with open("respuesta_GA.jsonl", mode='r') as archivo:
        for linea in archivo:
            li = linea.strip()
            data = json.loads(li)
            if prompt["id"] == data["data_id"]:
                return False
    return True

def llamadaThread(prompt):
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
        [Document] {prompt["text"]}
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

    data = response.json()
    if data.get("model"):
        raise Exception("No se encuentra la respuesta")

    respuesta = {
                    "data_id": prompt.get("id"),
                    "model": data.get("model"),
                    "resultado": data.get("choices", [{}])[0].get("message", {}).get("content"),
                    "usage": data.get("usage"),
                    "res_id": data.get("id")
                }

    with open("respuesta_GA.jsonl", mode='a') as archivo:
        archivo.write(json.dumps(respuesta) + "\n")
        print(respuesta)
    
    return respuesta

def principal_B():
    dataset = datasets.load_dataset(os.environ.get("PATH_DATASET"))
    prompt = list(dataset['test_coling2022'])

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for p in prompt:
            if verificar_nuevo(p):
                futures[executor.submit(llamadaThread, p)] = p

        for future in as_completed(futures):
            data_temp = futures[future]
            try:    
                data = future.result()
            except Exception as e:
                print(f'{data_temp.get("id")} a generado un error: {e}')
            else:
                print(f'{data_temp.get("id")} a generado los siguientes resultados: {data}')
    pass

async def llamada(sesion, semaforo, prompt):
    async with semaforo:
        # ta gordo la plantilla
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
        [Document] {prompt["summary"]}
        [Your response]"""

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

        try:
            async with sesion.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()
                respuesta = {
                    "data_id": prompt.get("id"),
                    "model": data.get("model"),
                    "resultado": data.get("choices", [{}])[0].get("message", {}).get("content"),
                    "usage": data.get("usage"),
                    "res_id": data.get("id")
                }

                async with aiofiles.open("respuesta_a.jsonl", mode='a') as archivo:
                    await archivo.write(json.dumps(respuesta) + "\n")

                print(f"respuesta guardada {prompt.get("id")}")
        except Exception as e:
            print(f"ocurrio un error en {prompt.get("id")}: {str(e)}")

async def principal_A():
    prompts = []
    with open(os.environ.get('DATA_JSON'), "r") as archivo:
        for linea in archivo:
            if linea.strip():
                prompts.append(json.loads(linea))

    semaforo = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as sesion:
        tasks = [llamada(sesion, semaforo, p) for p in prompts[11:20]]
        await asyncio.gather(*tasks)

    pass

if __name__ == "__main__":
    load_dotenv()
    # asyncio.run(principal_A())
    principal_B()