from pymongo import MongoClient
from config import uri,db_name

def get_database(uri:str,db_name:str):
    try:
        client = MongoClient(uri)
        return client[db_name]
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ao banco: {e}")