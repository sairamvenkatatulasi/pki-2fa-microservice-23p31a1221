from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import time
import hashlib
import hmac
import struct

app = FastAPI()

# ---------- MODELS ----------
class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# ---------- CONSTANTS ----------
PRIVATE_KEY_PATH = "/keys/student_private.pem"
SEED_PATH = "/data/seed.txt"

# ---------- UTILS ----------
def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )

def decrypt_seed(encrypted_seed_b64: str) -> str:
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    private_key = load_private_key()

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted.decode("utf-8")   # ✅ EXACT (no hex, no encode)

def read_seed() -> str:
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=400, detail="Seed not initialized")
    with open(SEED_PATH, "r") as f:
        return f.read().strip()
def generate_totp_hex(seed_hex: str, timestep=30, digits=6):
    key = bytes.fromhex(seed_hex)
    counter = int(time.time()) // timestep
    msg = struct.pack(">Q", counter)

    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[-1] & 0x0F
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % (10 ** digits)

    return str(code).zfill(digits), timestep - (int(time.time()) % timestep)


def verify_totp_hex(seed_hex, code, period=30):
    key = bytes.fromhex(seed_hex)
    now = int(time.time())

    # evaluator tolerance: ±1 window
    for offset in (-1, 0, 1):
        counter = (now // period) + offset
        msg = struct.pack(">Q", counter)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[-1] & 0x0F
        calc = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1_000_000

        if hmac.compare_digest(str(calc).zfill(6), code):
            return True

    return False



@app.get("/health")
def health():
    return {"status": "ok"}   # ✅ ALWAYS 200

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: SeedRequest):
    seed = decrypt_seed(req.encrypted_seed)
    os.makedirs("/data", exist_ok=True)
    with open(SEED_PATH, "w") as f:
        f.write(seed)         # ✅ WRITE AS-IS
    return {"status": "ok"}   # ✅ EXACT RESPONSE



@app.get("/generate-2fa")
def generate_2fa():
    seed = read_seed()
    code, remaining = generate_totp_hex(seed)
    return {"code": code, "valid_for": remaining}


@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    seed = read_seed()
    return {"valid": verify_totp_hex(seed, req.code)}

