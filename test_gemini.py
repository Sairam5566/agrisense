import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found")

if api_key:
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with different models
        models = ['gemini-1.5-flash', 'gemini-pro']
        
        for model_name in models:
            try:
                print(f"\nTesting {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, can you help with farming?")
                print(f"✓ {model_name} works: {response.text[:50]}...")
                break
            except Exception as e:
                print(f"✗ {model_name} failed: {str(e)}")
                
    except Exception as e:
        print(f"Configuration error: {str(e)}")
else:
    print("Please set GEMINI_API_KEY in your .env file")
