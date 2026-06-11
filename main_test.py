import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import datasets
from modelos import llamadaOpenRouter
from topicOP.utils import *


def verificar_nuevo(prompt, file_name):
    with open(file_name, mode='r') as archivo:
        for linea in archivo:
            li = linea.strip()
            data = json.loads(li)
            if prompt["id"] == data["data_id"]:
                return False
    return True

def organizador_prompt(texto, generation_prompt:str, topics_list):
    topic_str = "\n".join(
        [topic.split(":")[0].strip() for topic in topics_list]
    )
    generation_prompt.format(Document=texto, Topics=topic_str)
    return prompt

def generador_topics_aux(topics_root, topics_list, docs, seed_file, llamada, generation_prompt):

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for p in docs[400:410]:
            if verificar_nuevo(p):
                futures[executor.submit(llamada, p)] = p
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
    pass

def generador_topics(llamada, modelo, identificador, archivo_prompt, archivo_seed):
    dataset = datasets.load_dataset(os.environ.get("PATH_DATASET"))
    documentos = list(dataset['test_coling2022'])
    generation_prompt = open(archivo_prompt, "r").read()
    topic_root = TopicTree().from_seed_file(archivo_seed)
    topic_list = topic_root.to_topic_list(desc=True, count=False)

    generador_topics_aux(topic_root, topic_list, documentos, archivo_seed, llamada, generation_prompt)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for p in prompt[400:410]:
            if verificar_nuevo(p):
                futures[executor.submit(llamada, p)] = p
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
    dataset = datasets.load_dataset(os.environ.get("PATH_DATASET"), split="test_coling2022")
    prompt = list(dataset['text'])
    print(prompt)