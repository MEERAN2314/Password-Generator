from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from password_utils import (
    generate_random_password,
    generate_passphrase,
    generate_pin,
    check_password_strength,
    hash_password,
    validate_password_rules,
    generate_name_based_password
)

app = FastAPI(
    title="Password Generator API",
    description="A secure password generation and validation API with name-based options",
    version="1.2.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define all models first to avoid circular references
class ValidationRules(BaseModel):
    min_length: Optional[int] = None
    require_upper: Optional[bool] = None
    require_lower: Optional[bool] = None
    require_digit: Optional[bool] = None
    require_special: Optional[bool] = None

class PasswordRequest(BaseModel):
    length: int = 12
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_digits: bool = True
    include_special: bool = True
    exclude_similar: bool = True
    exclude_ambiguous: bool = True
    name_part1: Optional[str] = None
    name_part2: Optional[str] = None

class PassphraseRequest(BaseModel):
    word_count: int = 4
    separator: str = "-"
    capitalize: bool = True
    add_number: bool = True
    name_part1: Optional[str] = None
    name_part2: Optional[str] = None

class PinRequest(BaseModel):
    length: int = 6

class NameBasedRequest(BaseModel):
    name_part1: str
    name_part2: str = ""
    length: int = 12
    complexity: int = 2
    include_random: bool = True

class PasswordCheckRequest(BaseModel):
    password: str

class ValidationRequest(BaseModel):
    password: str
    rules: ValidationRules

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Password Generator API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/generate/password")
def generate_password(options: PasswordRequest):
    try:
        password = generate_random_password(
            length=options.length,
            include_uppercase=options.include_uppercase,
            include_lowercase=options.include_lowercase,
            include_digits=options.include_digits,
            include_special=options.include_special,
            exclude_similar=options.exclude_similar,
            exclude_ambiguous=options.exclude_ambiguous
        )
        strength = check_password_strength(password)
        return {
            "password": password,
            "strength": strength
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate/passphrase")
def generate_passphrase_endpoint(options: PassphraseRequest):
    try:
        passphrase = generate_passphrase(
            word_count=options.word_count,
            separator=options.separator,
            capitalize=options.capitalize,
            add_number=options.add_number,
            name_part1=options.name_part1,
            name_part2=options.name_part2
        )
        strength = check_password_strength(passphrase)
        return {
            "passphrase": passphrase,
            "strength": strength
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate/pin")
def generate_pin_endpoint(options: PinRequest):
    try:
        pin = generate_pin(options.length)
        return {"pin": pin}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate/name-based")
def generate_name_based(options: NameBasedRequest):
    try:
        password = generate_name_based_password(
            name_part1=options.name_part1,
            name_part2=options.name_part2,
            length=options.length,
            complexity=options.complexity,
            include_random=options.include_random
        )
        strength = check_password_strength(password)
        return {
            "password": password,
            "strength": strength
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/check-strength")
def check_strength(request: PasswordCheckRequest):
    try:
        return check_password_strength(request.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate")
def validate_password(request: ValidationRequest):
    try:
        return validate_password_rules(request.password, request.rules.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/hash")
def hash_password_endpoint(password: str, algorithm: str = "sha256"):
    try:
        return {"hash": hash_password(password, algorithm)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)