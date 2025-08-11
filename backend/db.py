from pymongo import MongoClient # Importando a classe MongoClient.
from config import *

# Conectando com o MongoDB Atlas.
def get_database(uri:str,db_name:str):
    client = MongoClient(uri)
    return client[db_name]
