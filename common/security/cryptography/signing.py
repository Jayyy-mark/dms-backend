from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Signer:
    @staticmethod
    def sign(private_key, message: str) -> bytes:
        return private_key.sign(
            message.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

    @staticmethod
    def verify(public_key, signature: bytes, message: str) -> bool:
        try:
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except:
            return False
