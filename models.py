from bson import ObjectId
from datetime import datetime
from db import *
from config import *
from pprint import pprint

db = get_database(db_name,client)

def find():
    try:
        # 1. Listar todas as coleções (tabelas) no banco de dados.
        collection_names = db.list_collection_names()
        if not collection_names:
            print("Nenhuma tabela encontrada no banco de dados.")
            return

        print("\nTabelas disponíveis no cluster:")
        for i, name in enumerate(collection_names, 1):
            print(f"{i}- {name}")

        # 2. Perguntar qual tabela o usuário deseja consultar.
        collection_choice = int(input("\nDigite o número da tabela que deseja consultar: "))
        if 1 <= collection_choice <= len(collection_names):
            selected_collection_name = collection_names[collection_choice - 1]
            collection = db[selected_collection_name]
        else:
            print("Seleção de tabela inválida.")
            return

        # 3. Listar todos os nomes na coleção selecionada.
        # Filtra para garantir que o documento tem a chave "nome"
        names = [doc.get("nome") for doc in collection.find({}, {"nome": 1, "_id": 0}) if doc.get("nome")]
        
        if not names:
            print(f"\nNenhum nome encontrado na tabela '{selected_collection_name}'.")
            return

        print(f"\nNomes disponíveis em '{selected_collection_name}':")
        for i, name in enumerate(names, 1):
            print(f"{i}- {name}")

        # 4. Perguntar qual nome o usuário deseja buscar.
        name_choice = int(input("\nDigite o número do nome para ver os detalhes: "))
        if 1 <= name_choice <= len(names):
            selected_name = names[name_choice - 1]
        else:
            print("Seleção de nome inválida.")
            return

        # 5. Realizar a busca final e exibir os dados.
        query = {"nome": selected_name}
        value = collection.find_one(query)

        if value:
            print("\n--- Dados encontrados ---")
            pprint(value)
            print("------------------------")
        else:
            raise FileNotFoundError(f"Cliente '{selected_name}' não encontrado na tabela '{selected_collection_name}'.")

    except ValueError:
        print("Entrada inválida. Por favor, insira um número.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def return_all():
    try:
        collection_names = db.list_collection_names()
        if not collection_names:
            print("Nenhuma tabela encontrada no banco de dados.")
            return

        print("\nTabelas disponíveis no cluster:")
        for i, name in enumerate(collection_names, 1):
            print(f"{i}- {name.capitalize()}")

        collection_choice = int(input("\nDigite o número da tabela que deseja consultar: "))
        if 1 <= collection_choice <= len(collection_names):
            selected_collection_name = collection_names[collection_choice - 1]
            collection = db[selected_collection_name]
        
            documents = list(collection.find())
            
            if not documents:
                print(f"\nNenhum documento encontrado na tabela '{selected_collection_name}'.")
                return

            print(f"\n--- Documentos encontrados em '{selected_collection_name}' ---")
            for doc in documents:
                pprint(doc)
                print("---")
            print(f"Total de {len(documents)} documento(s) encontrado(s).")
        else:
            print("Seleção de tabela inválida.")

    except ValueError:
        print("Entrada inválida. Por favor, insira um número.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def group():
    try:
        collection_names = db.list_collection_names()
        if not collection_names:
            print("Nenhuma tabela encontrada no banco de dados.")
            return

        print("\nTabelas disponíveis no cluster:")
        for i, name in enumerate(collection_names, 1):
            print(f"{i}- {name.capitalize()}")

        collection_choice = int(input("\nDigite o número da tabela que deseja consultar: "))
        if not (1 <= collection_choice <= len(collection_names)):
            print("Seleção de tabela inválida.")
            return
        
        selected_collection_name = collection_names[collection_choice - 1]
        collection = db[selected_collection_name]


        sample_document = collection.find_one()
        if not sample_document:
            print(f"A tabela '{selected_collection_name}' está vazia.")
            return

        fields = [field for field in sample_document.keys() if field != '_id']
        print(f"\nCampos disponíveis em '{selected_collection_name.capitalize()}':")
        for i, field in enumerate(fields, 1):
            print(f"{i}- {field}")

        field_choice = int(input("\nDigite o número do campo pelo qual você deseja filtrar: "))
        if not (1 <= field_choice <= len(fields)):
            print("Seleção de campo inválida.")
            return
        
        selected_field = fields[field_choice - 1]

        
        # Pega um documento que tenha o campo selecionado para análise
        doc_to_inspect = collection.find_one({selected_field: {"$exists": True}})
        field_value = doc_to_inspect.get(selected_field)

        if isinstance(field_value, list) and field_value and isinstance(field_value[0], dict):
            print(f"\nO campo '{selected_field}' contém sub-documentos. Vamos filtrar dentro dele.")
            
            # Pega os campos do primeiro sub-documento como exemplo
            sub_fields = list(field_value[0].keys())
            print(f"Campos disponíveis dentro de '{selected_field}':")
            for i, sub_field in enumerate(sub_fields, 1):
                print(f"{i}- {sub_field}")

            sub_field_choice = int(input("\nEscolha o número do sub-campo para filtrar: "))
            if not (1 <= sub_field_choice <= len(sub_fields)):
                print("Seleção de sub-campo inválida.")
                return
            
            selected_sub_field = sub_fields[sub_field_choice - 1]
            
            # Usa "dot notation" (notação de ponto) para acessar o valor do sub-campo
            key_for_distinct = f"{selected_field}.{selected_sub_field}"
            distinct_values = sorted(collection.distinct(key_for_distinct))
            
            final_query_key = key_for_distinct


        else:
            distinct_values = sorted(collection.distinct(selected_field))
            final_query_key = selected_field


        if not distinct_values:
            print(f"\nNão foram encontrados valores para o critério '{final_query_key}'.")
            return

        print(f"\nValores disponíveis para '{final_query_key}':")
        for i, value in enumerate(distinct_values, 1):
            print(f"{i}- {value}")

        value_choice = int(input(f"\nDigite o número do valor que você quer buscar: "))
        if not (1 <= value_choice <= len(distinct_values)):
            print("Seleção de valor inválida.")
            return
            
        selected_value = distinct_values[value_choice - 1]
        # Realiza a consulta com o valor selecionado

        query = {final_query_key: selected_value}
        results = list(collection.find(query))

        print(f"\n--- Documentos encontrados com '{final_query_key}: {selected_value}' ---")
        for doc in results:
            pprint(doc)
            print("---")
        
        print(f"Total de {len(results)} documento(s) encontrado(s).")
        print("----------------------------------------------------------------")

    except ValueError:
        print("Entrada inválida. Por favor, insira um número correspondente à opção.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def consulta():
    while True:
        print("\n--- Menu de Consultas ---")
        print("1- Buscar por nome específico")
        print("2- Listar todos os documentos da tabela")
        print("3- Agrupar dados por um campo")
        print("0- Fechar Consulta")
        
        try:
            opcao = int(input("\nEscolha uma opção: "))

            if opcao == 1:
                find()
            elif opcao == 2:
                return_all()
            elif opcao == 3:
                group()
            elif opcao == 0:
                print("Fechando o menu de consulta.")
                client.close()
                break
            else:
                print("Opção inválida. Tente novamente.")

        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado no menu de consulta: {e}")


# Criando o método de inserir.
def inserir():
    try:
        collection_names = db.list_collection_names()
        if not collection_names:
            print("Nenhuma tabela (coleção) encontrada no banco de dados.")
            return

        print("\nTabelas disponíveis no cluster:")
        for i, name in enumerate(collection_names, 1):
            print(f"{i}- {name.capitalize()}")

        collection_choice = int(input("\nDigite o número da tabela onde deseja inserir: "))
        if not (1 <= collection_choice <= len(collection_names)):
            print("Seleção de tabela inválida.")
            return
        
        selected_collection_name = collection_names[collection_choice - 1]
        collection = db[selected_collection_name]

        template_doc = collection.find_one()
        
        if not template_doc:
            print("Coleção vazia. Não há modelo para seguir. Por favor, insira manualmente.")
            # Você pode adicionar a lógica de inserção manual aqui se desejar
            return

        if '_id' in template_doc:
            del template_doc['_id']
            
        print(f"\n--- Preenchendo um novo documento para '{selected_collection_name.capitalize()}' ---")
        
        # Função auxiliar recursiva para preencher dados aninhados
        def preencher_campos(modelo, prefixo=""):
            dados_inseridos = {}
            for campo, valor_modelo in modelo.items():
                # 1. Verifica se é uma lista de sub-documentos
                if isinstance(valor_modelo, list) and valor_modelo and isinstance(valor_modelo[0], dict):
                    print(f"\n{prefixo}O campo '{campo}' é uma LISTA de sub-documentos.")
                    sub_template = valor_modelo[0] # Usa o primeiro item como modelo
                    lista_criada = []
                    for i in range(0,1):
                        print(f"\n{prefixo}--- Preenchendo '{campo}' ---")
                        # Chama a recursão para preencher cada item da lista
                        item_preenchido = preencher_campos(sub_template, prefixo + "  ")
                        lista_criada.append(item_preenchido)
                    
                    dados_inseridos[campo] = lista_criada

                # 2. Verifica se é um único sub-documento (objeto aninhado)
                elif isinstance(valor_modelo, dict):
                    print(f"\n{prefixo}Preenchendo o sub-documento '{campo}':")
                    # Chama a recursão para preencher o sub-documento
                    dados_inseridos[campo] = preencher_campos(valor_modelo, prefixo + "  ")

                # 3. Caso contrário, é um campo simples
                else:
                    valor_usuario = input(f"{prefixo}- Digite o valor para '{campo}': ")
                    dados_inseridos[campo] = valor_usuario
                    
            return dados_inseridos

        # Inicia o processo de preenchimento a partir do modelo principal
        data = preencher_campos(template_doc)

        if not data:
            print("Nenhum dado inserido. Operação cancelada.")
            return

        result = collection.insert_one(data)
        print("\nDocumento inserido com sucesso!")
        print("--- Documento Inserido ---")
        documento_inserido = collection.find_one({"_id": result.inserted_id})
        pprint(documento_inserido)
        print("--------------------------")

    except ValueError:
        print("Entrada inválida. Por favor, insira um número correspondente à opção.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# Criando a funcão de atualizar.
def atualizar():
    pass

# Criando a função de deletar.
def deletar():
    try:
        collection_names = db.list_collection_names()
        if not collection_names:
            print("Nenhuma tabela (coleção) encontrada no banco de dados.")
            return

        print("\nTabelas disponíveis no cluster:")
        for i, name in enumerate(collection_names, 1):
            print(f"{i}- {name.capitalize()}")

        collection_choice = int(input("\nDigite o número da tabela de onde deseja deletar: "))
        if 1 <= collection_choice <= len(collection_names):
            selected_collection_name = collection_names[collection_choice - 1]
            collection = db[selected_collection_name]
        else:
            print("Seleção de tabela inválida.")
            return

        # Busca todos os documentos da coleção e armazena em uma lista
        documents = list(collection.find({}))

        if not documents:
            print("Nenhum documento encontrado nesta coleção para deletar.")
            return

        print("\nDocumentos disponíveis para deleção:")
        for i, doc in enumerate(documents, 1):
            print(f"{i}- {doc}")

        doc_choice = int(input("\nDigite o número do documento que deseja deletar: "))
        if 1 <= doc_choice <= len(documents):
            # Pega o _id do documento escolhido para garantir que o correto seja deletado
            doc_to_delete = documents[doc_choice - 1]
            id_to_delete = doc_to_delete['_id']
            
            query = {"_id": id_to_delete}
            result = collection.delete_one(query)
            
            if result.deleted_count > 0:
                print(f"\nDocumento com ID '{id_to_delete}' deletado com sucesso.")
            else:
                # Esta mensagem é uma segurança, mas é improvável que ocorra nesta lógica
                print("Erro: Nenhum documento foi deletado.")
        else:
            print("Seleção de documento inválida.")

    except ValueError:
        print("Entrada inválida. Por favor, insira um número.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")