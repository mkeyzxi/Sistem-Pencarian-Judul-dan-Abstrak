import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

print(f"Model: {settings.GEMINI_MODEL}")
print(f"Max Tokens: {settings.LLM_MAX_TOKENS}")

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0.0,
    max_output_tokens=settings.LLM_MAX_TOKENS,
    google_api_key=settings.GEMINI_API_KEY,
)

print("\nTesting Prompt 1:")
try:
    res1 = llm.invoke("Tulis paragraf singkat tentang tomat.")
    print(repr(res1.content))
except Exception as e:
    print(f"Error: {e}")

print("\nTesting Prompt 2:")
try:
    res2 = llm.invoke("Tulis paragraf abstrak tentang daun tomat.")
    print(repr(res2.content))
except Exception as e:
    print(f"Error: {e}")
