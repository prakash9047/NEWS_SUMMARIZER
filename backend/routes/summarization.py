from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    max_length: int = 150
    target_lang: str = "en"

class TextResponse(BaseModel):
    summary: Optional[str] = None
    translation: Optional[str] = None

async def call_groq_api(prompt: str, task_type: str = "translation") -> str:
    """
    Call Groq API with a prompt and return the response
    task_type: either "translation" or "summarization" to optimize model choice
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GROQ_API_KEY not configured"
            )

        # Choose model based on task
        model = "llama-3.1-8b-instant"  # Faster model for quick responses
        if task_type == "translation":
            model = "llama-3.3-70b-versatile"  # More accurate model for translations

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional translator and summarizer. Provide ONLY the requested output without any explanations or notes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": model,
            "temperature": 0.3,
            "max_tokens": 1000,
            "top_p": 0.9
        }
        
        logger.info(f"Calling Groq API with model: {model}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                logger.error(f"Groq API error: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Groq API error: {error_detail}"
                )
    except httpx.TimeoutException:
        logger.error("Request to Groq API timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to Groq API timed out"
        )
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calling Groq API: {str(e)}"
        )

@router.post("/text")
async def process_text(request: TextRequest):
    try:
        # First, generate summary if text is longer than max_length
        summary = ""
        if len(request.text) > request.max_length:
            summary_prompt = f"""Summarize the following text in about {request.max_length} characters:

{request.text}

Provide ONLY the summary, no additional text."""
            
            summary = await call_groq_api(summary_prompt, "summarization")

        # Then, translate if target language is not English
        translation = ""
        if request.target_lang.lower() != "en":
            language_prompts = {
                'ar': 'Modern Standard Arabic',
                'bn': 'Standard Bengali',
                'zh': 'Simplified Chinese',
                'fr': 'French',
                'de': 'German',
                'hi': 'Hindi',
                'id': 'Indonesian',
                'it': 'Italian',
                'ja': 'Japanese',
                'ko': 'Korean',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'es': 'Spanish',
                'tr': 'Turkish'
            }

            target_language = language_prompts.get(
                request.target_lang.lower(),
                request.target_lang.upper()
            )
            
            translation_prompt = f"""Translate this text to {target_language}. Maintain the original meaning and tone:

{request.text}

Provide ONLY the translation in {target_language}, no other text."""

            translation = await call_groq_api(translation_prompt, "translation")

        response = {
            "summary": summary if summary else None,
            "translation": translation if translation else None
        }
        
        logger.info(f"Successfully processed text. Response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/url")
async def process_url(url: str):
    try:
        # Fetch content from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            text = response.text
            
        # Process the text content
        return await process_text(TextRequest(text=text))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing URL: {str(e)}"
        ) 