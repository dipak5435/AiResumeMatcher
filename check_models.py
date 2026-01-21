import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")

genai.configure(api_key=api_key)

print("\n📋 Available models for generateContent:")
print("-" * 50)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

print("\nTrying to use 'models/gemini-pro'...")
try:
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content("Hello")
    print("✓ models/gemini-pro works!")
except Exception as e:
    print(f"❌ Error: {e}")
