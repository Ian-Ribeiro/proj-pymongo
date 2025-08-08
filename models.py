from bson import ObjectId
from datetime import datetime
from pprint import pprint
from pymongo import MongoClient
from config import db_name, uri
from db import get_database

class MercadoDB:
    def __init__(self):
        # cria o client e conecta
        self.client = MongoClient(uri)
        self.db = get_database(uri, db_name)

    # ---------------- CONSULTAS ----------------
    def find(self):
        """Busca por nome específico"""
        try:
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada no banco de dados.")
                return

            print("\nTabelas disponíveis no cluster:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name}")

            collection_choice = int(input("\nDigite o número da tabela que deseja consultar: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção de tabela inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]

            names = [doc.get("nome") for doc in collection.find({}, {"nome": 1, "_id": 0}) if doc.get("nome")]
            if not names:
                print("Nenhum nome encontrado nesta tabela.")
                return

            print("\nNomes disponíveis:")
            for i, name in enumerate(names, 1):
                print(f"{i}- {name}")

            name_choice = int(input("\nDigite o número do nome para ver os detalhes: "))
            if not (1 <= name_choice <= len(names)):
                print("Seleção inválida.")
                return

            query = {"nome": names[name_choice - 1]}
            value = collection.find_one(query)

            if value:
                print("\n--- Dados encontrados ---")
                pprint(value)
            else:
                print("Cliente não encontrado.")

        except ValueError:
            print("Entrada inválida. Digite um número.")
        except Exception as e:
            print(f"Erro: {e}")

    def return_all(self):
        """Lista todos os documentos de uma tabela"""
        try:
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada no banco de dados.")
                return

            print("\nTabelas disponíveis no cluster:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name.capitalize()}")

            collection_choice = int(input("\nDigite o número da tabela que deseja consultar: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]
            documents = list(collection.find())

            if not documents:
                print("Nenhum documento encontrado.")
                return

            print(f"\n--- Documentos em '{collection.name}' ---")
            for doc in documents:
                pprint(doc)
                print("---")
            print(f"Total: {len(documents)} documento(s).")

        except ValueError:
            print("Entrada inválida. Digite um número.")
        except Exception as e:
            print(f"Erro: {e}")

    def group(self):
        """Agrupa dados por campo"""
        try:
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada no banco de dados.")
                return

            print("\nTabelas disponíveis no cluster:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name.capitalize()}")

            collection_choice = int(input("\nDigite o número da tabela: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]
            sample_document = collection.find_one()
            if not sample_document:
                print("Tabela vazia.")
                return

            fields = [f for f in sample_document.keys() if f != '_id']
            print("\nCampos disponíveis:")
            for i, field in enumerate(fields, 1):
                print(f"{i}- {field}")

            field_choice = int(input("\nEscolha o campo para filtrar: "))
            if not (1 <= field_choice <= len(fields)):
                print("Seleção inválida.")
                return

            selected_field = fields[field_choice - 1]
            distinct_values = sorted(collection.distinct(selected_field))

            print(f"\nValores de '{selected_field}':")
            for i, value in enumerate(distinct_values, 1):
                print(f"{i}- {value}")

            value_choice = int(input("\nEscolha o valor: "))
            if not (1 <= value_choice <= len(distinct_values)):
                print("Seleção inválida.")
                return

            query = {selected_field: distinct_values[value_choice - 1]}
            results = list(collection.find(query))

            print(f"\nDocumentos com '{selected_field}':")
            for doc in results:
                pprint(doc)
                print("---")
            print(f"Total: {len(results)} documento(s).")

        except ValueError:
            print("Entrada inválida.")
        except Exception as e:
            print(f"Erro: {e}")

    def consulta(self):
        """Menu de consultas"""
        while True:
            print("\n--- Menu de Consultas ---")
            print("1- Buscar por nome específico")
            print("2- Listar todos os documentos")
            print("3- Agrupar por campo")
            print("0- Sair")

            try:
                opcao = int(input("\nEscolha: "))
                if opcao == 1:
                    self.find()
                elif opcao == 2:
                    self.return_all()
                elif opcao == 3:
                    self.group()
                elif opcao == 0:
                    print("Encerrando consulta...")
                    self.client.close()
                    break
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Digite um número válido.")

    # ---------------- INSERÇÃO ----------------
    def inserir(self):
        try:
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada.")
                return

            print("\nTabelas disponíveis:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name.capitalize()}")

            collection_choice = int(input("\nDigite o número da tabela: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]
            template_doc = collection.find_one()

            if not template_doc:
                print("Coleção vazia. Insira manualmente.")
                return

            if '_id' in template_doc:
                del template_doc['_id']

            def preencher_campos(modelo):
                dados = {}
                for campo, valor_modelo in modelo.items():
                    if isinstance(valor_modelo, dict):
                        print(f"Sub-documento '{campo}':")
                        dados[campo] = preencher_campos(valor_modelo)
                    elif isinstance(valor_modelo, list) and valor_modelo and isinstance(valor_modelo[0], dict):
                        lista = [preencher_campos(valor_modelo[0])]
                        dados[campo] = lista
                    else:
                        dados[campo] = input(f"- {campo}: ")
                return dados

            data = preencher_campos(template_doc)
            result = collection.insert_one(data)
            print("\nDocumento inserido com sucesso!")
            pprint(collection.find_one({"_id": result.inserted_id}))

        except ValueError:
            print("Entrada inválida.")
        except Exception as e:
            print(f"Erro: {e}")

    # ---------------- ATUALIZAÇÃO ----------------
        # ---------------- ATUALIZAÇÃO ----------------
    def atualizar(self):
        """Atualiza um campo específico de um documento"""
        try:
            # 1. Listar tabelas
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada no banco de dados.")
                return

            print("\nTabelas disponíveis:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name.capitalize()}")

            collection_choice = int(input("\nDigite o número da tabela: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]

            # 2. Listar documentos
            documents = list(collection.find())
            if not documents:
                print("Nenhum documento encontrado nesta tabela.")
                return

            print("\nDocumentos disponíveis:")
            for i, doc in enumerate(documents, 1):
                print(f"{i}- {doc}")

            doc_choice = int(input("\nDigite o número do documento que deseja atualizar: "))
            if not (1 <= doc_choice <= len(documents)):
                print("Seleção inválida.")
                return

            selected_doc = documents[doc_choice - 1]

            # 3. Listar campos do documento
            fields = [field for field in selected_doc.keys() if field != "_id"]
            print("\nCampos disponíveis para atualização:")
            for i, field in enumerate(fields, 1):
                print(f"{i}- {field}: {selected_doc[field]}")

            field_choice = int(input("\nDigite o número do campo que deseja atualizar: "))
            if not (1 <= field_choice <= len(fields)):
                print("Seleção inválida.")
                return

            selected_field = fields[field_choice - 1]

            # 4. Novo valor
            new_value = input(f"Digite o novo valor para '{selected_field}': ")

            # 5. Atualizar no banco
            result = collection.update_one(
                {"_id": selected_doc["_id"]},
                {"$set": {selected_field: new_value}}
            )

            if result.modified_count > 0:
                print("\nDocumento atualizado com sucesso!")
                pprint(collection.find_one({"_id": selected_doc["_id"]}))
            else:
                print("Nenhuma modificação foi feita.")

        except ValueError:
            print("Entrada inválida. Digite um número.")
        except Exception as e:
            print(f"Erro: {e}")

    # ---------------- DELEÇÃO ----------------
    def deletar(self):
        try:
            collection_names = self.db.list_collection_names()
            if not collection_names:
                print("Nenhuma tabela encontrada.")
                return

            print("\nTabelas disponíveis:")
            for i, name in enumerate(collection_names, 1):
                print(f"{i}- {name.capitalize()}")

            collection_choice = int(input("\nDigite o número da tabela: "))
            if not (1 <= collection_choice <= len(collection_names)):
                print("Seleção inválida.")
                return

            collection = self.db[collection_names[collection_choice - 1]]
            documents = list(collection.find())

            if not documents:
                print("Nenhum documento encontrado.")
                return

            for i, doc in enumerate(documents, 1):
                print(f"{i}- {doc}")

            doc_choice = int(input("\nDigite o número do documento: "))
            if not (1 <= doc_choice <= len(documents)):
                print("Seleção inválida.")
                return

            id_to_delete = documents[doc_choice - 1]['_id']
            result = collection.delete_one({"_id": id_to_delete})

            if result.deleted_count > 0:
                print("Documento deletado com sucesso.")
            else:
                print("Erro ao deletar documento.")

        except ValueError:
            print("Entrada inválida.")
        except Exception as e:
            print(f"Erro: {e}")


# Exemplo de uso:
if __name__ == "__main__":
    mercado = MercadoDB()
    mercado.consulta()
