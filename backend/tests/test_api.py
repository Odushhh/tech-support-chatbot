import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.data.storage import data_storage
from backend.app.main import app
from backend.app.nlp.engine import nlp_engine
from backend.app.nlp.semantic_search import semantic_search

client = TestClient(app)

@pytest.fixture(scope="module")
def test_data():
    # Setup test data
    data_storage.clear()
    data_storage.store_interaction("test_query", "test_response")
    data_storage.store_feedback("test_query_id", 5, "   eat response!")
    semantic_search.build_index([
        {"id": "1", "content": "This is a test document"},
        {"id": "2", "content": "Another test document"}
    ])
    yield
    # Teardown
    data_storage.clear()

@pytest.fixture(scope="module")
def test_token():
    return create_access_token(subject="testuser")

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Technical Support Chatbot API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    response = client.post("/api/chat", json={"query": "How does this work?"})
    if response.status_code != 200:
        print("Error details:", response.json())

    assert response.status_code == 200
    assert "response" in response.json()
    assert "intent" in response.json()

def test_chat_endpoint_empty_query():
    response = client.post("/api/chat", json={"query": ""})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_feedback_endpoint(test_data):
    response = client.post("/api/feedback", json={
        "query_id": "test_query_id",
        "rating": 4,
        "comment": "Good response"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Feedback received successfully"}

def test_feedback_endpoint_invalid_data():
    response = client.post("/api/feedback", json={
        "query_id": "test_query_id",
        "rating": 6,  # Invalid rating
        "comment": "Good response"
    })
    assert response.status_code == 400
    assert "detail" in response.json()

def test_popular_topics_endpoint(test_data):
    response = client.get("/api/popular-topics")
    assert response.status_code == 200
    assert "topics" in response.json()

def test_search_endpoint(test_data):
    response = client.get("/api/search?query=test document")
    assert response.status_code == 200
    assert "results" in response.json()
    assert len(response.json()["results"]) > 0

def test_login_endpoint():
    response = client.post("/api/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_login_endpoint_invalid_credentials():
    response = client.post("/api/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "detail" in response.json()

def test_protected_endpoint(test_token):
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    assert "message" in response.json()

def test_protected_endpoint_no_token():
    response = client.get("/api/protected")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_rate_limiting():
    for _ in range(settings.RATE_LIMIT + 1):
        response = client.get("/api/rate-limited")
        if response.status_code == 429:
            assert "detail" in response.json()
            return
    pytest.fail("Rate limiting did not trigger")

@pytest.mark.parametrize("query,expected_intent", [
    ("How do I reset my password?", "password_reset"),
    ("What are your business hours?", "business_hours"),
    ("I can't log into my account", "login_issues"),
])
def test_intent_detection(query, expected_intent):
    intent = nlp_engine.detect_intent(query)
    assert intent == expected_intent

def test_answer_generation():
    query = "How do I update my profile?"
    answer = nlp_engine.generate_response(query, "profile_update")
    assert isinstance(answer, str)
    assert len(answer) > 0

def test_entity_recognition():
    text = "I bought a new iPhone 12 last week"
    entities = nlp_engine.extract_entities(text)
    assert isinstance(entities, list)
    assert any(entity["type"] == "PRODUCT" for entity in entities)

def test_sentiment_analysis():
    text = "I'm really happy with the service!"
    sentiment = nlp_engine.analyze_sentiment(text)
    assert sentiment in ["positive", "negative", "neutral"]

def test_text_summarization():
    long_text = "..." # A long piece of text
    summary = nlp_engine.summarize_text(long_text)
    assert isinstance(summary, str)
    assert len(summary) < len(long_text)

def test_language_detection():
    text = "Bonjour, comment allez-vous?"
    language = nlp_engine.detect_language(text)
    assert language == "fr"
    
def test_data_storage():
    data_storage.store_interaction("test_query", "test_response")
    interactions = data_storage.get_interactions()
    assert len(interactions) > 0
    assert any(interaction["query"] == "test_query" for interaction in interactions)

def test_semantic_search():
    query = "test document"
    results = semantic_search.search(query)
    assert isinstance(results, list)
    assert len(results) > 0



def test_error_handling():
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    assert "detail" in response.json()

if __name__ == "__main__":
    pytest.main([__file__])
