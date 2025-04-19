from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from dotenv import load_dotenv
import os
from datetime import datetime
import httpx
import json
import logging
from gtts import gTTS
import io
from backend.models import NewsArticle, UserInteraction
from backend.schemas import NewsArticleCreate, NewsArticleResponse
from backend.database import get_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

def get_newsapi_client() -> Optional[NewsApiClient]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key or api_key == "your_news_api_key_here":
        logger.error("NEWS_API_KEY not found in environment variables")
        return None
    
    try:
        client = NewsApiClient(api_key=api_key)
        # Test the API key by making a simple request
        test_response = client.get_top_headlines(language='en', country='us', page_size=1)
        if test_response.get('status') == 'error':
            logger.error(f"News API key validation failed: {test_response.get('message')}")
            return None
        logger.info("News API key validated successfully")
        return client
    except Exception as e:
        logger.error(f"Error creating News API client: {str(e)}")
        return None

def parse_datetime(date_str: str) -> datetime:
    try:
        if not date_str:
            return datetime.utcnow()
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing datetime {date_str}: {str(e)}")
        return datetime.utcnow()

async def call_groq_api(prompt: str, model: str = "mixtral-8x7b-v0.1") -> str:
    """Call Groq API with a prompt and return the response"""
    if not prompt:
        return ""
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return prompt

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional translator and summarizer. Provide accurate and natural translations while maintaining the original meaning."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": model,
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
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
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return prompt
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        return prompt

async def translate_text(text: str, target_lang: str) -> str:
    """Translate text using Groq API with language-specific instructions"""
    if not text:
        return ""
    
    language_prompts = {
        'ar': 'Translate to Modern Standard Arabic:',
        'bn': 'Translate to Standard Bengali:',
        'zh': 'Translate to Simplified Chinese:',
        'en': 'Translate to English:',
        'fr': 'Translate to French:',
        'de': 'Translate to German:',
        'hi': 'Translate to Hindi:',
        'id': 'Translate to Indonesian:',
        'it': 'Translate to Italian:',
        'ja': 'Translate to Japanese:',
        'ko': 'Translate to Korean:',
        'pt': 'Translate to Portuguese:',
        'ru': 'Translate to Russian:',
        'es': 'Translate to Spanish:',
        'tr': 'Translate to Turkish:'
    }
    
    prompt = f"""{language_prompts.get(target_lang, f'Translate to {target_lang}:')}

{text}

Translate the above text naturally and accurately, maintaining the original meaning and tone."""
    
    return await call_groq_api(prompt)

async def summarize_text(text: str, max_length: int = 150) -> str:
    """Summarize text using Groq API"""
    if not text:
        return ""
    
    prompt = f"""Summarize the following text in about {max_length} characters. Provide ONLY the summary, no explanations:

{text}"""
    
    return await call_groq_api(prompt)

async def process_article(article: NewsArticle, db: Session):
    """Process article for translation and summarization"""
    try:
        # Summarize description
        if article.description and not article.summary:
            article.summary = await summarize_text(article.description)
        
        # Translate title and description
        if article.title and not article.translated_title:
            article.translated_title = await translate_text(article.title)
        
        if article.description and not article.translated_description:
            article.translated_description = await translate_text(article.description)
        
        db.add(article)
        try:
            db.commit()
            db.refresh(article)
        except Exception as db_error:
            logger.error(f"Database error while processing article: {str(db_error)}")
            db.rollback()
    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")

async def text_to_speech(text: str, lang: str = 'en') -> bytes:
    """Convert text to speech using gTTS"""
    try:
        # Map language codes to gTTS compatible codes
        lang_map = {
            'en': 'en',
            'hi': 'hi',
            'ar': 'ar',
            'bn': 'bn',
            'zh': 'zh-CN',
            'fr': 'fr',
            'de': 'de',
            'id': 'id',
            'it': 'it',
            'ja': 'ja',
            'ko': 'ko',
            'pt': 'pt',
            'ru': 'ru',
            'es': 'es',
            'tr': 'tr'
        }
        
        # Get the correct language code or default to English
        tts_lang = lang_map.get(lang.lower(), 'en')
        logger.info(f"Converting text to speech in language: {tts_lang}")
        
        # Create gTTS object
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Save to bytes buffer
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return fp.read()
    except Exception as e:
        logger.error(f"Error in text to speech conversion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert text to speech: {str(e)}"
        )

@router.get("/latest", response_model=List[NewsArticleResponse])
async def get_latest_news(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        newsapi = get_newsapi_client()
        if not newsapi:
            logger.error("NEWS_API_KEY not configured")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NEWS_API_KEY not configured. Please add your News API key to the .env file."
            )

        logger.info("Fetching latest news from News API")
        top_headlines = newsapi.get_top_headlines(
            language='en',
            country='us',
            page_size=10
        )
        
        if not top_headlines.get('articles'):
            logger.warning("No articles found in API response")
            return []
        
        articles = []
        for article_data in top_headlines['articles']:
            try:
                if not all([article_data.get('title'), article_data.get('url')]):
                    logger.warning(f"Skipping article with missing title or URL: {article_data}")
                    continue
                    
                # Check for existing article
                existing_article = db.query(NewsArticle).filter(NewsArticle.url == article_data['url']).first()
                if existing_article:
                    articles.append(existing_article)
                    continue
                
                # Create new article
                article = NewsArticle(
                    title=article_data['title'],
                    description=article_data.get('description') or "No description available",
                    url=article_data['url'],
                    image_url=article_data.get('urlToImage'),
                    published_at=parse_datetime(article_data.get('publishedAt')),
                    source=article_data.get('source', {}).get('name', 'Unknown'),
                    category="general"
                )
                db.add(article)
                articles.append(article)
                
                # Add background task for processing
                background_tasks.add_task(process_article, article, db)
            except Exception as article_error:
                logger.error(f"Error processing article data: {str(article_error)}")
                continue
        
        try:
            db.commit()
            # Refresh all new articles to get their IDs
            for article in articles:
                db.refresh(article)
            logger.info(f"Successfully processed {len(articles)} articles")
            return articles
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
            
    except NewsAPIException as api_error:
        logger.error(f"News API error: {str(api_error)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"News API error: {str(api_error)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_latest_news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/category/{category}", response_model=List[NewsArticleResponse])
async def get_news_by_category(category: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        newsapi = get_newsapi_client()
        if not newsapi:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NEWS_API_KEY not configured. Please add your News API key to the .env file."
            )

        valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        if category.lower() not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
            
        category_news = newsapi.get_top_headlines(
            category=category.lower(),
            language='en',
            country='us',
            page_size=10
        )
        
        if not category_news.get('articles'):
            logger.warning(f"No articles found for category: {category}")
            return []
        
        articles = []
        for article_data in category_news['articles']:
            try:
                if not all([article_data.get('title'), article_data.get('url')]):
                    continue
                    
                # Check for existing article
                existing_article = db.query(NewsArticle).filter(NewsArticle.url == article_data['url']).first()
                if existing_article:
                    articles.append(existing_article)
                    continue
                
                # Create new article
                article = NewsArticle(
                    title=article_data['title'],
                    description=article_data.get('description') or "No description available",
                    url=article_data['url'],
                    image_url=article_data.get('urlToImage'),
                    published_at=parse_datetime(article_data.get('publishedAt')),
                    source=article_data.get('source', {}).get('name', 'Unknown'),
                    category=category.lower()
                )
                db.add(article)
                articles.append(article)
                
                # Add background task for processing
                background_tasks.add_task(process_article, article, db)
            except Exception as article_error:
                logger.error(f"Error processing article data: {str(article_error)}")
                continue
        
        try:
            db.commit()
            # Refresh all new articles to get their IDs
            for article in articles:
                db.refresh(article)
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )
            
        return articles
    except NewsAPIException as api_error:
        logger.error(f"News API error: {str(api_error)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"News API error: {str(api_error)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_news_by_category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/saved", response_model=List[NewsArticleResponse])
async def get_saved_news(db: Session = Depends(get_db)):
    try:
        articles = db.query(NewsArticle).order_by(NewsArticle.created_at.desc()).all()
        return articles
    except Exception as e:
        logger.error(f"Error fetching saved news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saved news"
        )

@router.post("/interaction")
async def record_interaction(
    interaction: dict,
    db: Session = Depends(get_db)
):
    try:
        new_interaction = UserInteraction(
            article_id=interaction["article_id"],
            interaction_type=interaction["interaction_type"],
            interaction_weight=1.0 if interaction["interaction_type"] == "view" else 2.0
        )
        db.add(new_interaction)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record interaction"
        )

@router.get("/recommended/{user_id}", response_model=List[NewsArticleResponse])
async def get_recommended_news(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        # Get user's interaction history
        interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        # Get categories and sources the user has interacted with
        user_categories = set()
        user_sources = set()
        
        for interaction in interactions:
            article = db.query(NewsArticle).filter(NewsArticle.id == interaction.article_id).first()
            if article:
                user_categories.add(article.category)
                user_sources.add(article.source)
        
        # Get recent articles from user's preferred categories and sources
        recommended_articles = []
        if user_categories or user_sources:
            articles_query = db.query(NewsArticle)
            if user_categories:
                articles_query = articles_query.filter(NewsArticle.category.in_(user_categories))
            if user_sources:
                articles_query = articles_query.filter(NewsArticle.source.in_(user_sources))
            
            recommended_articles = articles_query.order_by(NewsArticle.published_at.desc()).limit(10).all()
        
        # If no recommendations based on history, return latest news
        if not recommended_articles:
            recommended_articles = db.query(NewsArticle).order_by(
                NewsArticle.published_at.desc()
            ).limit(10).all()
        
        return recommended_articles
    except Exception as e:
        logger.error(f"Error getting recommended news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommended news"
        )

@router.post("/text-to-speech")
async def get_speech(
    text: str = Body(...),
    language: str = Body("en")
):
    """Convert text to speech and return audio file"""
    try:
        logger.info(f"Received text-to-speech request for language: {language}")
        audio_data = await text_to_speech(text, language)
        
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        logger.error(f"Error in text to speech endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 