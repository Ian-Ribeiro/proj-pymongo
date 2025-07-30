from bson import ObjectId
from models import *

def main():
    choice = int(input("------------------------------------------------\n1- Consulta\n2- Inserir\n3- Deletar\n------------------------------------------------\nEscolha uma opção: "))

    match choice:
        case 1:
            consulta()

        case 2:
            inserir()

        case 3:
            deletar()

if __name__ == "__main__":
    main()