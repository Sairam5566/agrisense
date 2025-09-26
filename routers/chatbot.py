from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

router = APIRouter()

# Get API key and validate
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logging.warning("GEMINI_API_KEY not found in environment variables")

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        user_message = chat_message.message
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # Validate API key
        if not API_KEY:
            raise HTTPException(
                status_code=401, 
                detail="GEMINI_API_KEY is missing. Please add it to your .env file and restart the server."
            )
        
        # Create a system prompt for agriculture-focused responses
        system_prompt = """You are an AI assistant specialized in agriculture and farming. 
        You help farmers with crop management, pest control, weather advice, fertilizer recommendations, 
        and general farming practices. Keep your responses helpful, practical, and focused on agriculture.
        If asked about non-agricultural topics, politely redirect to farming-related assistance.
        Provide concise, actionable advice in 2-3 sentences."""
        
        # Try different model names with fallback (corrected model names)
        model_names = ["gemini-2.5-flash"]
        ai_response = None
        
        for model_name in model_names:
            try:
                # Initialize the model
                model = genai.GenerativeModel(model_name)
                
                # Combine system prompt with user message
                full_prompt = f"{system_prompt}\n\nUser question: {user_message}"
                
                # Generate response
                response = model.generate_content(full_prompt)
                
                if response.text:
                    ai_response = response.text
                    break
            except Exception as model_error:
                logging.warning(f"Model {model_name} failed: {str(model_error)}")
                continue
        
        if not ai_response:
            ai_response = "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        
        return ChatResponse(
            response=ai_response,
            status="success"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_message = str(e)
        logging.error(f"Chatbot error: {error_message}")
        
        if any(keyword in error_message.lower() for keyword in ["api_key_invalid", "invalid api key", "authentication", "unauthorized"]):
            raise HTTPException(
                status_code=401, 
                detail="Invalid API key. Please check your Gemini API key configuration."
            )
        elif any(keyword in error_message.lower() for keyword in ["quota", "limit", "rate"]):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Chatbot service error: {error_message}"
            )
