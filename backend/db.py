from pymongo import MongoClient # Importando a classe MongoClient.
from config import uri,db_name

# Conectando com o MongoDB Atlas.
def get_database(uri:str,db_name:str):
    try:
        client = MongoClient(uri)
        return client[db_name]
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ao banco: {e}")