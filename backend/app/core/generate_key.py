import secrets
import base64
import os
from dotenv import load_dotenv, set_key

load_dotenv()

def generate_secret_key(length=32):
    """Generate a secure secret key."""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')

def store_secret_key(secret_key):
    env_path = os.path.join('D:/IS-Project/chatbot-v11/backend/.env')

    try:
        # Load existing .env file
        load_dotenv(env_path)
        
        # Set or update the SECRET_KEY
        set_key(env_path, "SECRET_KEY", secret_key)
        
        print("SECRET_KEY added/updated in the .env file! Check the path:", {env_path})
    except FileNotFoundError:
        print(f"Error: .env file not found at {env_path}")
    except PermissionError:
        print(f"Error: Permission denied. Could not access or write to {env_path}")

if __name__ == "__main__":
    secret_key = generate_secret_key()
    store_secret_key(secret_key)
    print(f"Generated secret key: {secret_key}")