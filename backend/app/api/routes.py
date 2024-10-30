from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from backend.app.core.chatbot import TechSupportChatbot
from app.data.storage import DataStorage
from nlp.engine import NLPEngine
from utils.helpers import rate_limit, log_request
from backend.app.core.config import Settings
from backend.app.data.fetcher import DataFetcher
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
chatbot = TechSupportChatbot()
data_storage = DataStorage()
nlp_engine = NLPEngine()
data_fetcher = DataFetcher()

class Query(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str
    confidence: float
    sources: List[str]

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int
    comment: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
@rate_limit(max_calls=5, time_frame=60)
async def chat(query: Query, background_tasks: BackgroundTasks, settings: Settings = Depends(Settings)):
    try:
        # Log the incoming request
        background_tasks.add_task(log_request, query.text)

        # Process the query
        response, confidence, sources = chatbot.process_query(query.text)

        # Store the interaction for future analysis
        background_tasks.add_task(data_storage.store_interaction, query.text, response)

        return ChatResponse(response=response, confidence=confidence, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Users can submit feedback on chatbot's responses
@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    try:
        data_storage.store_feedback(feedback.query_id, feedback.rating, feedback.comment)
        return JSONResponse(content={"message": "Feedback received successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve popular topics based on user interactions
@router.get("/popular_topics")
async def get_popular_topics():
    try:
        topics = data_storage.get_popular_topics()
        return JSONResponse(content={"topics": topics}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Train the NLP model
@router.post("/retrain")
async def retrain_model(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(nlp_engine.retrain_model)
        return JSONResponse(content={"message": "Model retraining initiated"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Check on chatbot's performance
@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)

# Retrieve usage stats
@router.get("/stats")
async def get_stats():
    try:
        stats = data_storage.get_usage_stats()
        return JSONResponse(content=stats, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update chatbot's knowledge base
@router.post("/update_knowledge_base")
async def update_knowledge_base(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(chatbot.update_knowledge_base)
        return JSONResponse(content={"message": "Knowledge base update initiated"}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search for issues across all platforms
@router.get("/search_issues")
async def search_issues(query: str, platform: str = "all", limit: int = 10):
    try:
        results = chatbot.search_issues(query, platform, limit)
        return JSONResponse(content={"results": results}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suggest a solution based on user's query
@router.post("/suggest_solution")
async def suggest_solution(query: Query):
    try:
        solution = chatbot.suggest_solution(query.text)
        return JSONResponse(content={"solution": solution}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch all relevant data for a given query from various sources.
@router.get("/fetch_all_data")
async def fetch_all_data(query: str):
    try:
        data = data_fetcher.fetch_all_data(query)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch data from StackOverflow through the StackExchangeAPI and index into Elasticsearch.
@router.get("/fetch_stackoverflow_data")
async def fetch_stackoverflow_data(query: str, limit: int = 5):
    try:
        data = data_fetcher.fetch_stackoverflow_data(query, limit)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch issues from GitHub and index them into Elasticsearch.
@router.get("/fetch_github_issues")
async def fetch_github_issues(query: str, limit: int = 5):
    try:
        data = data_fetcher.fetch_github_issues(query, limit)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch and index relevant documentation into Elasticsearch.
@router.get("/fetch_documentation")
async def fetch_documentation(query: str):
    try:
        data = data_fetcher.fetch_documentation(query)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
