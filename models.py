from bson import ObjectId # Importando o ObjectId para gerar id's automaticamente.
from datetime import datetime # Importando datetime que representa data e hora.
from db import *
from config import *
from pprint import pprint

class DataMecardo:
    # Vriando o metódo init.
    def __init__(self, db_name:str, client):
        self.client = client
        self.db = get_database(db_name,client)
        coll_nome = input("- Informe o nome da coleção: ")
        self.collection = self.db[coll_nome]
        print(f"Nome Coleção: {coll_nome}")

    # Criando o método de inserir.
    def inserir(self):
        pass

    # Criando o método de consulta.
    def consulta(self):
        pass

    # Criando o método de atualização.
    def atualizacao(self):
        pass

    # Criando o método de remoção.
    def remocao(self):
        pass

    def find(self):
        colection_filmes = self.db['clientes']
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

    def menu(self):
        opc = input("-Escolha uma opção: ")
        while True:
            match opc:
                case 1:
                    self.inserir()
                case 2:
                    pass
                case 3:
                    pass
                case 4:
                    pass
                case 5:
                    break