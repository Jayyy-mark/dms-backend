from cryptography.fernet import Fernet

class KeyManager:
    @staticmethod
    def save_key(file_path: str, key: bytes):
        with open(file_path, 'wb') as f:
            f.write(key)

    @staticmethod
    def load_key(file_path: str) -> bytes:
        with open(file_path, 'rb') as f:
            return f.read()
