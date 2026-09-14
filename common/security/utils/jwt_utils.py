# common/security/utils/jwt_utils.py
import jwt
from django.conf import settings

def verify_jwt(token: str) -> dict:
    signing_key = getattr(settings, "SIMPLE_JWT", {}).get("SIGNING_KEY", settings.SECRET_KEY)
    
    # Try decoding with SimpleJWT signing key first
    try:
        return jwt.decode(token, signing_key, algorithms=["HS256"])
    except Exception:
        pass

    # Try JWT_SECRET_KEY if defined and different
    jwt_key = getattr(settings, "JWT_SECRET_KEY", None)
    if jwt_key and jwt_key != signing_key:
        try:
            return jwt.decode(token, jwt_key, algorithms=["HS256"])
        except Exception:
            pass

    raise Exception("Invalid or expired JWT token")
