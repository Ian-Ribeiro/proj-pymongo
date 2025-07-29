from bson import ObjectId
from models import *

def main():
    choice = int(input("------------------------------------------------\n1- Consulta\n"))

    match choice:
        case 1:
            consulta()

if __name__ == "__main__":
    main()