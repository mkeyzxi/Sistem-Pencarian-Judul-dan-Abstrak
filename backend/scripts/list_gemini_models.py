import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found in .env")
    sys.exit(1)

import google.generativeai as genai
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f" - {m.name}")
