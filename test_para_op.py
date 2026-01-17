import asyncio
import aiohttp
import json
import aiofiles
import os
from concurrent.futures import ThreadPoolExecutor

DATA_JSON = "datasets/bills_train.jsonl"

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

                async with aiofiles.open("Salida.jsonl", mode='a') as archivo:
                    await archivo.write(json.dumps(respuesta) + "\n")

                print(f"respuesta guardada {prompt.get("id")}")
        except Exception as e:
            print(f"ocurrio un error en {prompt.get("id")}: {str(e)}")

async def principal_A():
    prompt = []
    with open(DATA_JSON, "r") as archivo:
        for linea in archivo:
            if linea.strip():
                prompt.append(json.loads(linea))

    semaforo = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as sesion:
        tasks = [llamada(sesion, semaforo, p) for p in prompt[0:10]]
        await asyncio.gather(*tasks)

    pass

if __name__ == "__main__":
    asyncio.run(principal_A())