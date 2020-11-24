from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json


# https://cryptobook.nakov.com/asymmetric-key-ciphers/rsa-encrypt-decrypt-examples
class RSAUtils:
    def __init__(self):
        self.key_pair = self.generate_key_pair()
        self.pub_key = self.key_pair.publickey()

    def generate_key_pair(size=1024):
        return RSA.generate(1024)

    def encrypt_str(self, msg):
        msg = msg.encode('utf-8')
        encryptor = PKCS1_OAEP.new(self.pub_key)
        return encryptor.encrypt(msg)

    def encrypt_json(self, json_msg):
        msg = json.dumps(json_msg)
        return self.encrypt_str(msg)

    def decrypt_str(self, encrypted):
        decryptor = PKCS1_OAEP.new(self.key_pair)
        return decryptor.decrypt(encrypted)

    def decrypt_json(self, encrypted):
        decrypted = self.decrypt_str(encrypted)
        return json.loads(decrypted)
