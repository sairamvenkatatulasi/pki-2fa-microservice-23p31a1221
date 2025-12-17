import base64
import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import pyotp
import time  # add this at top of file
DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"

def decrypt_seed(encrypted_seed_b64: str, private_key_path: str = "student_private.pem") -> str:
    import base64
    encrypted_seed_b64 = encrypted_seed_b64.strip()
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    with open(private_key_path, "rb") as f:
        key = RSA.import_key(f.read())

    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
    seed_bytes = cipher.decrypt(encrypted_bytes)

    seed_hex_full = seed_bytes.hex()
    seed_hex = seed_hex_full[:64]  # keep first 32 bytes (64 hex chars)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEED_FILE.write_text(seed_hex)
    return seed_hex




def read_seed() -> str:
    if not SEED_FILE.exists():
        raise FileNotFoundError("Seed not initialized. Call /decrypt-seed first.")
    return SEED_FILE.read_text().strip()

def seed_to_base32(seed_hex: str) -> str:
    raw = bytes.fromhex(seed_hex)
    b32 = base64.b32encode(raw).decode("ascii").strip("=")
    return b32


def generate_totp(seed_hex: str) -> tuple[str, int]:
    b32 = seed_to_base32(seed_hex)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    code = totp.now()
    now = int(time.time())
    remaining = totp.interval - (now % totp.interval)
    return code, int(remaining)


def verify_totp(seed_hex: str, code: str) -> bool:
    b32 = seed_to_base32(seed_hex)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.verify(code, valid_window=1)
