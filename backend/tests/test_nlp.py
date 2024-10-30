import os

import pytest

from backend.app.core.config import settings
from backend.app.nlp.engine import nlp_engine
from backend.app.nlp.semantic_search import semantic_search
from backend.app.utils.helpers import sanitize_input

# Example usage of settings
print(f"App Name: {settings.APP_NAME}")
print(f"Debug mode: {settings.DEBUG}")

# Example usage of sanitize_input
test_input = "<script>alert('XSS');</script>"
sanitized = sanitize_input(test_input)
print(f"Sanitized input: {sanitized}")

@pytest.fixture(scope="module")
def setup_test_data():
    # Setup test data for semantic search
    documents = [
        {"id": "1", "content": "How to reset your password"},
        {"id": "2", "content": "Troubleshooting login issues"},
        {"id": "3", "content": "Setting up two-factor authentication"},
        {"id": "4", "content": "Updating your account information"},
        {"id": "5", "content": "Understanding our refund policy"}
    ]
    semantic_search.build_index(documents)
    yield
    semantic_search.clear_index()

# Can the model correctly identify intent in a user's query?
def test_intent_detection():
    queries = [
        ("How do I reset my password?", "password_reset"),
        ("I can't log in to my account", "login_issues"),
        ("What's your refund policy?", "refund_policy"),
        ("How do I update my email address?", "account_settings"),
        ("Is there a mobile app available?", "app_inquiry")
    ]
    for query, expected_intent in queries:
        intent = nlp_engine.detect_intent(query)
        print(f"Query: {query}, Detected Intent: {intent}, Expected: {expected_intent}")
        assert intent == expected_intent, f"Expected {expected_intent} for query '{query}', but got {intent}"

# Can the model correctly identify entities within text?
def test_entity_recognition():
    text = "I bought an iPhone 12 Pro last week and it's not turning on"
    entities = nlp_engine.extract_entities(text)

    print(f"Extracted entities: {entities}")

    product_found = any(entity["type"] == "PRODUCT" and entity["text"] == "iPhone 12 Pro" for entity in entities)
    assert product_found, "Expected 'iPhone 12 Pro' to be recognized as a PRODUCT entity."

    date_found = any(entity["type"] == "DATE" and "last week" in entity["text"] for entity in entities)
    assert date_found, "Expected 'last week' to be recognized as a DATE entity"

    # assert any(entity["type"] == "PRODUCT" and entity["text"] == "iPhone 12 Pro" for entity in entities)
    # assert any(entity["type"] == "DATE" and "last week" in entity["text"] for entity in entities)

# Can the model retrieve documents related to a user's query?
def test_semantic_search(setup_test_data):
    query = "How do I change my password?"
    results = semantic_search.search(query)
    assert len(results) > 0
    assert any("reset your password" in result['content'].lower() for result in results)

# Can the model verify if text inputs are correctly classified?
def test_text_classification():
    texts = [
        ("I love this product! It's amazing!", "positive"),
        ("This is the worst experience I've ever had.", "negative"),
        ("The package arrived on time and in good condition.", "neutral")
    ]
    labels = [
        ("Customer Feedback"),
        ("Customer Feedback"),
        ("Customer Feedback")
    ]
    predicted_label, confidence = nlp_engine.classify_text(text, labels)
    assert predicted_label in labels, f"Expected one of {labels}, but got {predicted_label}."
    assert confidence > 0.5, "Expected confidence to be greater than 0.5."
    
    for text, expected_class in texts:
        classified = nlp_engine.classify_text(text, labels)
        assert classified == expected_class, f"Expected {expected_class} for text '{text}', but got {classified}"

# Can the model calculate similarity between texts?
def test_text_similarity():
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "A fast auburn canine leaps above an idle hound"
    text3 = "Python is a popular programming language"
    
    similarity_1_2 = nlp_engine.calculate_similarity(text1, text2)
    similarity_1_3 = nlp_engine.calculate_similarity(text1, text3)
    
    assert similarity_1_2 > 0.5  # Texts 1 and 2 should be quite similar
    assert similarity_1_3 < 0.5  # Texts 1 and 3 should not be very similar

# Can the model extract key words from text inputs?
def test_keyword_extraction():
    text = "Artificial intelligence and machine learning are transforming the technology industry."
    keywords = nlp_engine.extract_keywords(text, top_k=5)

    assert "artificial intelligence" in keywords, "Expected 'artificial intelligence' to be in the extracted keywords."
    assert "machine learning" in keywords, "Expected 'machine learning' to be in the extracted keywords."
    assert "technology" in keywords, "Expected 'technology' to be in the extracted keywords."

# Can the model generate text based on a user's prompt
def test_text_generation():
    prompt = "Once upon a time, in a land far away"
    generated_text = nlp_engine.generate_text(prompt, max_length=100)

    print(f"Generated text: {generated_text}")
    assert generated_text, "Generated text should not be empty"
    assert prompt in generated_text, "Generated text should contain the prompt."

    assert len(generated_text) > len(prompt)
    assert prompt in generated_text
    assert len(generated_text.split()) <= 100  # Check if the generated text respects the max_length
    
def test_question_answering():
    context = """
    The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. 
    It is named after the engineer Gustave Eiffel, whose company designed and built the tower. 
    Constructed from 1887 to 1889 as the entrance arch to the 1889 World's Fair, it was initially criticized 
    by some of France's leading artists and intellectuals for its design, but it has become a global 
    cultural icon of France and one of the most recognizable structures in the world.
    """
    questions = [
        ("Where is the Eiffel Tower located?", "Paris, France"),
        ("Who designed the Eiffel Tower?", "Gustave Eiffel"),
        ("When was the Eiffel Tower built?", "1887 to 1889")
    ]
    for question, expected_answer in questions:
        answer = nlp_engine.answer_question(context, question)
        assert expected_answer.lower() in answer.lower(), f"Expected '{expected_answer}' in answer to '{question}', but got '{answer}'"


'''
# Extra functionality test
def test_sentiment_analysis():
    positive_text = "I'm really happy with the excellent service I received!"
    negative_text = "This product is terrible and the customer support is even worse."
    neutral_text = "The sky is blue and the grass is green."

    assert nlp_engine.analyze_sentiment(positive_text) == "positive"
    assert nlp_engine.analyze_sentiment(negative_text) == "negative"
    assert nlp_engine.analyze_sentiment(neutral_text) == "neutral"

# Extra
def test_language_detection():
    texts = [
        ("Hello, how are you?", "en"),
        ("Bonjour, comment allez-vous?", "fr"),
        ("Hola, ¿cómo estás?", "es"),
        ("Guten Tag, wie geht es Ihnen?", "de"),
        ("こんにちは、お元気ですか？", "ja")
    ]
    for text, expected_lang in texts:
        detected_lang = nlp_engine.detect_language(text)
        assert detected_lang == expected_lang, f"Expected {expected_lang} for text '{text}', but got {detected_lang}"

# Extra
def test_text_summarization():
    long_text = """
    Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence 
    concerned with the interactions between computers and human language, in particular how to program computers 
    to process and analyze large amounts of natural language data. The goal is a computer capable of understanding 
    the contents of documents, including the contextual nuances of the language within them. The technology can then 
    accurately extract information and insights contained in the documents as well as categorize and organize the 
    documents themselves.
    """
    summary = nlp_engine.summarize_text(long_text)
    assert len(summary) < len(long_text)
    assert "Natural Language Processing" in summary
    assert "computers" in summary
    assert "language" in summary

# Extra
def test_named_entity_linking():
    text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
    linked_entities = nlp_engine.link_entities(text)
    assert any(entity["text"] == "Apple Inc." and entity["type"] == "ORGANIZATION" for entity in linked_entities)
    assert any(entity["text"] == "Steve Jobs" and entity["type"] == "PERSON" for entity in linked_entities)
    assert any(entity["text"] == "Cupertino" and entity["type"] == "LOCATION" for entity in linked_entities)
    assert any(entity["text"] == "California" and entity["type"] == "LOCATION" for entity in linked_entities)

# Extra
def test_spelling_correction():
    misspelled_texts = [
        ("I recieved your mesage", "I received your message"),
        ("The wether is nice today", "The weather is nice today"),
        ("She is very intellegent", "She is very intelligent")
    ]
    for misspelled, correct in misspelled_texts:
        corrected = nlp_engine.correct_spelling(misspelled)
        assert corrected.lower() == correct.lower(), f"Expected '{correct}' but got '{corrected}'"

# Extra
def test_grammar_checking():
    texts = [
        ("She don't like ice cream", ["She doesn't like ice cream"]),
        ("The cats is sleeping", ["The cats are sleeping", "The cat is sleeping"]),
        ("I seen the movie yesterday", ["I saw the movie yesterday", "I have seen the movie yesterday"])
    ]
    for incorrect, possible_corrections in texts:
        suggestions = nlp_engine.check_grammar(incorrect)
        assert any(correction in suggestions for correction in possible_corrections), f"Expected one of {possible_corrections} in suggestions for '{incorrect}', but got {suggestions}"

'''


# Model to run checks on all specified NLP functions at once
def test_nlp_pipeline():
    text = "Apple Inc. is planning to release a new iPhone model next month, according to industry insiders."
    result = nlp_engine.process_text(text)
    
    assert "entities" in result
    # assert "sentiment" in result
    assert "keywords" in result
    # assert "summary" in result
    # assert "language" in result

    assert any(entity["text"] == "Apple Inc." and entity["type"] == "ORGANIZATION" for entity in result["entities"])
    # assert any(entity["text"] == "iPhone" and entity["type"] == "PRODUCT" for entity in result["entities"])
    assert result["sentiment"] in ["positive", "negative", "neutral"]
    assert "Apple" in result["keywords"] and "iPhone" in result["keywords"]
    # assert len(result["summary"]) < len(text)
    # assert result["language"] == "en"

if __name__ == "__main__":
    pytest.main([__file__])

