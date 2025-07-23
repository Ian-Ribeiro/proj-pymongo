from pymongo.server_api import ServerApi
from pymongo import MongoClient # Importando a classe MongoClient.
from config import *

client = MongoClient(uri,server_api=ServerApi('1'))
# Conectando com o MongoDB Atlas.
def get_database(db_name:str,client):
    client = client
    return client[db_name]
