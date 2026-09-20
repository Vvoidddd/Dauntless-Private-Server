"""Password and opaque bearer-token primitives."""
import base64, hashlib, hmac, secrets

SCRYPT_N, SCRYPT_R, SCRYPT_P, KEY_BYTES = 1 << 14, 8, 1, 32

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=KEY_BYTES)
    return "scrypt${}${}${}${}${}".format(SCRYPT_N, SCRYPT_R, SCRYPT_P, base64.urlsafe_b64encode(salt).decode(), base64.urlsafe_b64encode(derived).decode())

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if algorithm != "scrypt" or (int(n), int(r), int(p)) != (SCRYPT_N, SCRYPT_R, SCRYPT_P): return False
        decoded_salt = base64.urlsafe_b64decode(salt)
        decoded_expected = base64.urlsafe_b64decode(expected)
        if len(decoded_salt) != 16 or len(decoded_expected) != KEY_BYTES: return False
        actual = hashlib.scrypt(password.encode(), salt=decoded_salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=KEY_BYTES)
        return hmac.compare_digest(actual, decoded_expected)
    except (ValueError, TypeError): return False

def new_session_token() -> str: return secrets.token_urlsafe(32)
def hash_token(token: str) -> str: return hashlib.sha256(token.encode("utf-8")).hexdigest()
