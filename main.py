from db import *
from config import *
from models import MercadoDB  # importa a classe com os métodos do CRUD

def main():
    mercado = MercadoDB()  # cria o objeto que controla o banco

    while True:
        try:
            choice = int(input(
                "------------------------------------------------\n"
                "1- Consulta\n"
                "2- Inserir\n"
                "3- Deletar\n"
                "4- Atualizar\n"
                "0- Sair\n"
                "------------------------------------------------\n"
                "Escolha uma opção: "
            ))

            match choice:
                case 1:
                    mercado.consulta()
                case 2:
                    mercado.inserir()
                case 3:
                    mercado.deletar()
                case 4:
                    mercado.atualizar()
                case 0:
                    print("Saindo...")
                    break
                case _:
                    print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

if __name__ == "__main__":
    main()
