from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {
    "admin": "adminpass",
    "eng_user": "engpass",
    "contract_user": "conpass",
    "legal_user": "legalpass",
    "complaint_user": "comppass"
}

print("--- CORRECT PASSWORD HASHES ---")
for username, password in users.items():
    hashed_password = pwd_context.hash(password)
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print(f"Correct Hash: {hashed_password}")
    print("-" * 20)

    