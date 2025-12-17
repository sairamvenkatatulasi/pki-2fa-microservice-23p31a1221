from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crypto_utils import decrypt_seed, read_seed, generate_totp, verify_totp

app = FastAPI()

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.get("/health")
def health():
    # If seed exists, return 200 else 400 as per task
    try:
        read_seed()
        return {"status": "ok"}
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Seed not initialized")

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptRequest):
    try:
        seed_hex = decrypt_seed(body.encrypted_seed)
        return {"status": "success", "seed_len": len(seed_hex)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/generate-2fa")
def generate_2fa():
    try:
        seed_hex = read_seed()
        code, remaining = generate_totp(seed_hex)
        return {"code": code, "valid_for": remaining}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class VerifyRequest(BaseModel):
    code: str

@app.post("/verify-2fa")
def verify_2fa(body: VerifyRequest):
    seed_hex = read_seed()
    valid = verify_totp(seed_hex, body.code)
    return {"valid": valid}
