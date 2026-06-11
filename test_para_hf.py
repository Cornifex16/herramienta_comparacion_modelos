import json
import os
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
    
    cliente = InferenceClient(
        api_key=os.environ.get("HF_TOKEN")
    )
    chat_completion = cliente.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[
            {
                "role": "user",
                "content": Template
            }
        ],
    )
    respuesta = {
                    "data_id": prompt.get("id"),
                    "model": chat_completion.model,
                    "resultado": chat_completion.choices[0].message.content,
                    "usage": chat_completion.usage.model_dump(),
                    "res_id": chat_completion.id
                }
    with open("respuesta_GA.jsonl", mode='a') as archivo:
        archivo.write(json.dumps(respuesta) + "\n")
        print(respuesta)
    return respuesta

def main():
    dataset = datasets.load_dataset(os.environ.get("PATH_DATASET"))
    prompt = list(dataset['test_coling2022'])

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for p in prompt[400:410]:
            if verificar_nuevo(p):
                futures[executor.submit(llamadaThread, p)] = p
        # futures = {executor.submit(llamadaThread, p): p for p in prompt[0:20]}
        for future in as_completed(futures):
            data_temp = futures[future]
            try:    
                data = future.result()
            except Exception as e:
                print(f'{data_temp.get("id")} a generado un error: {e}')
            else:
                print(f'{data_temp.get("id")} a generado los siguientes resultados: {data}')
    pass

if __name__ == "__main__":
    load_dotenv()
    main()