import os

import pytest

from backend.app.core.chatbot import TechSupportChatbot
from backend.app.core.config import settings
from backend.app.data.storage import data_storage
from backend.app.nlp.engine import nlp_engine
from backend.app.utils.helpers import sanitize_input


@pytest.fixture(scope="module")
def chatbot():
    return TechSupportChatbot()

@pytest.fixture(scope="module")
def setup_test_data():
    # Setup test data
    data_storage.clear()
    data_storage.store_interaction("How do I reset my password?", "To reset your password, please follow these steps: 1. Go to the login page. 2. Click on 'Forgot Password'. 3. Enter your email address. 4. Follow the instructions sent to your email.")
    data_storage.store_interaction("What are your business hours?", "Our business hours are Monday to Friday, 9 AM to 5 PM EST.")
    yield
    # Teardown
    data_storage.clear()

def test_chatbot_initialization(chatbot):
    assert isinstance(chatbot, TechSupportChatbot)
    assert chatbot.nlp_engine == nlp_engine

def test_chatbot_greet(chatbot):
    greeting = chatbot.greet()
    assert isinstance(greeting, str)
    assert len(greeting) > 0

def test_chatbot_farewell(chatbot):
    farewell = chatbot.farewell()
    assert isinstance(farewell, str)
    assert len(farewell) > 0

def test_chatbot_process_query(chatbot, setup_test_data):
    query = "How do I reset my password?"
    response = chatbot.process_query(query)
    assert isinstance(response, dict)
    assert "response" in response
    assert "intent" in response
    assert "confidence" in response
    assert response["intent"] == "password_reset"

def test_chatbot_handle_unknown_query(chatbot):
    query = "What is the meaning of life?"
    response = chatbot.process_query(query)
    assert isinstance(response, dict)
    assert "response" in response
    assert "I'm sorry, I don't have information about that" in response["response"]

def test_chatbot_context_awareness(chatbot):
    query1 = "What are your business hours?"
    response1 = chatbot.process_query(query1)
    assert "business hours" in response1["response"].lower()
    
    query2 = "Are you open on weekends?"
    response2 = chatbot.process_query(query2)
    assert "weekend" in response2["response"].lower() or "saturday" in response2["response"].lower() or "sunday" in response2["response"].lower()

@pytest.mark.parametrize("query,expected_intent", [
    ("How do I change my email?", "account_settings"),
    ("I can't log in to my account", "login_issues"),
    ("Do you offer refunds?", "refund_policy"),
    ("Where can I download the software?", "software_download"),
    ("Is there a mobile app available?", "mobile_app"),
])
def test_chatbot_intent_detection(chatbot, query, expected_intent):
    response = chatbot.process_query(query)
    assert response["intent"] == expected_intent

def test_chatbot_sentiment_analysis(chatbot):
    positive_query = "I love your product, it's amazing!"
    positive_response = chatbot.process_query(positive_query)
    assert positive_response["sentiment"] == "positive"

    negative_query = "This is terrible, I'm very disappointed."
    negative_response = chatbot.process_query(negative_query)
    assert negative_response["sentiment"] == "negative"

def test_chatbot_entity_recognition(chatbot):
    query = "I bought the XYZ-1000 model last week and it's not working"
    response = chatbot.process_query(query)
    assert "entities" in response
    assert any(entity["type"] == "PRODUCT" and entity["text"] == "XYZ-1000" for entity in response["entities"])

def test_chatbot_language_detection(chatbot):
    english_query = "How can I contact customer support?"
    english_response = chatbot.process_query(english_query)
    assert english_response["language"] == "en"

    spanish_query = "¿Cómo puedo contactar al servicio al cliente?"
    spanish_response = chatbot.process_query(spanish_query)
    assert spanish_response["language"] == "es"

def test_chatbot_input_sanitization(chatbot):
    malicious_query = "<script>alert('XSS')</script>How do I reset my password?"
    sanitized_query = sanitize_input(malicious_query)
    response = chatbot.process_query(sanitized_query)
    assert "<script>" not in response["response"]

def test_chatbot_response_generation(chatbot):
    query = "What's your return policy?"
    response = chatbot.process_query(query)
    assert len(response["response"]) <= settings.MAX_RESPONSE_LENGTH

def test_chatbot_feedback_handling(chatbot):
    query = "How do I upgrade my account?"
    response = chatbot.process_query(query)
    feedback = chatbot.handle_feedback(response["id"], 4, "Very helpful, thanks!")
    assert feedback["message"] == "Feedback received successfully"

def test_chatbot_conversation_history(chatbot):
    chatbot.process_query("Hello")
    chatbot.process_query("How are you?")
    history = chatbot.get_conversation_history()
    assert len(history) == 2
    assert history[0]["query"] == "Hello"
    assert history[1]["query"] == "How are you?"

def test_chatbot_rate_limiting(chatbot):
    for _ in range(settings.RATE_LIMIT):
        chatbot.process_query("Test query")
    
    with pytest.raises(Exception) as excinfo:
        chatbot.process_query("Rate limit exceeded query")
    assert "Rate limit exceeded" in str(excinfo.value)

def test_chatbot_error_handling(chatbot):
    # Simulate an error in the NLP engine
    def mock_process_query(query):
        raise Exception("NLP Engine Error")
    
    original_process_query = nlp_engine.process_query
    nlp_engine.process_query = mock_process_query
    
    response = chatbot.process_query("Test error handling")
    assert "An error occurred" in response["response"]
    
    # Restore the original method
    nlp_engine.process_query = original_process_query

if __name__ == "__main__":
    pytest.main([__file__])

