import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.config import settings
from langchain_groq import ChatGroq

print(f"Model: {settings.GROQ_MODEL}")
print(f"Max Tokens: {settings.LLM_MAX_TOKENS}")

llm = ChatGroq(
    model=settings.GROQ_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKENS,
    groq_api_key=settings.GROQ_API_KEY,
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
