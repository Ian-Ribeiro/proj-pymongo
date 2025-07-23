from bson import ObjectId # Importando o ObjectId para gerar id's automaticamente.
from datetime import datetime # Importando datetime que representa data e hora.
from db import *
from config import *
from pprint import pprint

db = get_database(db_name,client)

# Criando o método de inserir.
def inserir():
    pass

# Criando o método de consulta.
def consulta():
    pass

# Criando o método de atualização.
def atualizacao():
    pass

# Criando o método de remoção.
def remocao():
    pass

def find():
    colection_filmes = db['clientes']
    query = {"nome": "Ana Silva"}

    try:
        filme = colection_filmes.find_one(query)
        if filme:
            print(" Client encontrado")
            pprint(filme)
        else:
            print("Nenhum client encontrado!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        client.close()