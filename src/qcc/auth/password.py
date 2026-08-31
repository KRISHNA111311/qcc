from passlib.context import CryptContext

# Use sha256_crypt – no 72-byte limit
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password = password.strip()
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    plain = plain.strip()
    return pwd_context.verify(plain, hashed)