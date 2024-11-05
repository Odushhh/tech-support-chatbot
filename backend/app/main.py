import logging
import typing
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.api.routes import router as api_router
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.core.security import create_access_token
from backend.app.data.storage import data_storage
from backend.app.nlp.engine import nlp_engine
from backend.app.nlp.semantic_search import semantic_search
from backend.app.utils.helpers import sanitize_input
from typing import Any

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("tech-support-chatbot-v2/backend/app/static", StaticFiles(directory="tech-support-chatbot-v2/backend/app/static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    # Initialize data storage
    data_storage.connect()
    # Load NLP models
    nlp_engine.load_models()
    # Build semantic search index
    documents = data_storage.get_all_documents()
    semantic_search.build_index(documents)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")
    # Close data storage connection
    data_storage.disconnect()

@app.get("/")
async def root():
    return {"message": "Welcome to the Technical Support Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        query = sanitize_input(data.get("query", ""))
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Process the query
        intent = nlp_engine.detect_intent(query)
        response = nlp_engine.generate_response(query, intent)
        
        # Log the interaction
        data_storage.store_interaction(query, response)
        return {"response": response, "intent": intent}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/feedback")
async def feedback(request: Request):
    try:
        data = await request.json()
        query_id = data.get("query_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not query_id or rating is None:
            raise HTTPException(status_code=400, detail="Query ID and rating are required")

        # Store the feedback
        data_storage.store_feedback(query_id, rating, comment)

        return {"message": "Feedback received successfully"}
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/popular-topics")
async def popular_topics():
    try:
        topics = data_storage.get_popular_topics()
        return {"topics": topics}
    except Exception as e:
        logger.error(f"Error in popular-topics endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/search")
async def search(query: str):
    try:
        sanitized_query = sanitize_input(query)
        results = semantic_search.search(sanitized_query)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")

        # Authenticate user (implement your own authentication logic)
        if authenticate_user(username, password):
            access_token = create_access_token(data={"sub": username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def authenticate_user(username: str, password: str) -> bool:
    # Implement your user authentication logic here
    # This is just a placeholder
    return username == "admin" and password == "password"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

logger.info("Main application module loaded successfully")
