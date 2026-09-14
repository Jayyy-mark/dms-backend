from cryptography.fernet import Fernet

class SymmetricCrypto:
    @staticmethod
    def generate_key() -> bytes:
        return Fernet.generate_key()

    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(token: str, key: bytes) -> str:
        f = Fernet(key)
        return f.decrypt(token.encode()).decode()
