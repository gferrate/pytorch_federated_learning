from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP, AES
import json
import requests
import logging


# https://cryptobook.nakov.com/asymmetric-key-ciphers/rsa-encrypt-decrypt-examples
# https://pycryptodome.readthedocs.io/en/latest/src/examples.html
class RSAUtils:
    def __init__(self):
        self.key_pair = self.generate_key_pair()
        self.pub_key = self.key_pair.publickey()
        self.public_keys = {}

    @staticmethod
    def generate_key_pair():
        return RSA.generate(1024)

    def export_public_key(self):
        return self.pub_key.export_key().decode('utf8')

    def encrypt_bytes(self, data, pub_key=None, host=None, port=None):
        if pub_key and host and port:
            raise Exception(
                'Args mutually exclusive. '
                'Either pub_key or (host and port) must be set')
        elif host and port:
            pub_key = self.get_or_set_pub_key(host, port)
        else:
            pub_key = pub_key or self.pub_key

        # Generate session key
        session_key = get_random_bytes(16)
        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(pub_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        return (enc_session_key, cipher_aes.nonce, tag, ciphertext)

    def encrypt_str(self, msg, pub_key=None, host=None, port=None):
        msg = msg.encode('utf-8')
        return self.encrypt_bytes(msg, pub_key, host, port)

    def encrypt_json(self, json_msg, pub_key=None, host=None, port=None):
        msg = json.dumps(json_msg)
        return self.encrypt_str(msg, pub_key)

    def decrypt_bytes(self, encrypted_data):
        enc_session_key, nonce, tag, ciphertext = encrypted_data

        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(self.key_pair)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data

    def decrypt_str(self, encrypted):
        decrypted = self.decrypt_bytes(encrypted)
        return decrypted.decode('utf8')

    def decrypt_json(self, encrypted):
        decrypted = self.decrypt_bytes(encrypted)
        return json.loads(decrypted)

    def get_pub_key(self, host, port):
        logging.info(
            'Getting key for host: {} and port: {}'.format(host, port))
        url = 'http://{}:{}/pub_key'.format(host, port)
        try:
            res = requests.get(url=url)
            pub_key = res.json()['pub_key']
            pub_key = RSA.import_key(pub_key)
        except Exception as e:
            logging.error('Error getting pub key from {}'.format(url),
                          exc_info=True)
            raise e
        return pub_key

    def get_or_set_pub_key(self, host, port):
        dict_key = (host, port)
        # Check if cached
        if dict_key in self.public_keys:
            return self.public_keys[dict_key]
        # Else query it
        self.public_keys[dict_key] = self.get_pub_key(host, port)
        return self.public_keys[dict_key]
