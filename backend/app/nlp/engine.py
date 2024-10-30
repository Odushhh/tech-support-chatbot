import os
import logging
from typing import List, Dict, Any, Tuple
from transformers import pipeline, DistilBertTokenizerFast, AutoModelForMaskedLM, AutoModelForSequenceClassification, AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from backend.app.core.config import settings
from backend.app.utils.helpers import sanitize_input

logger = logging.getLogger(__name__)

class NLPEngine:
    def __init__(self):
        # self.intent_classifier = pipeline("sentiment-analysis", model=settings.INTENT_CLASSIFICATION_MODEL)
        # self.qa_model = pipeline("question-answering", model=settings.QA_MODEL)
        # self.sentiment_analyzer = pipeline("sentiment-analysis", model=settings.SENTIMENT_ANALYSIS_MODEL)
        # self.summarizer = pipeline("summarization", model=settings.SUMMARIZATION_MODEL)
        # self.sentence_transformer = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)

        self.nlp_model = AutoModelForMaskedLM.from_pretrained("distilbert/distilroberta-base")
        self.intent_classifier = AutoModelForSequenceClassification.from_pretrained(os.getenv("FEATURE_EXTRACTION_MODEL"))
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(os.getenv("TOKENIZER"))
        self.qa_model = AutoModelForQuestionAnswering.from_pretrained(os.getenv("QA_MODEL"))
        self.sentiment_analyzer = AutoModelForSequenceClassification.from_pretrained(os.getenv("SENTIMENT_ANALYSIS_MODEL"))
        self.summarizer = AutoModelForSeq2SeqLM.from_pretrained(os.getenv("SUMMARIZATION_MODEL"))
        self.sentence_transformer = SentenceTransformer(os.getenv("SENTENCE_TRANSFORMER_MODEL"))

        # Load custom models if specified
        if settings.CUSTOM_INTENT_MODEL:
            self.custom_intent_tokenizer = pipeline("text-classification", model=settings.CUSTOM_INTENT_MODEL)
            self.custom_intent_model = pipeline("text-classification", model=settings.CUSTOM_INTENT_MODEL)

    # Detect the intent of the user's query.
    def detect_intent(self, query: str) -> str:
        try:
            sanitized_query = sanitize_input(query)
            inputs = self.tokenizer(query, padding=True, truncation=True, return_tensors="pt")
            # outputs = self.nlp_model(**inputs)
            self.nlp_model(**inputs)

            if settings.INTENT_CLASSIFICATION_MODEL:
                return self._custom_intent_detection(sanitized_query)
            else:
                result = self.intent_classifier(sanitized_query)[0]
                print(f"Detected intent: {result['label']}, Score: {result['score']}")

                intent_threshold = getattr(settings, 'INTENT_CLASSIFICATION_THRESHOLD', 0.7)
                print(f"Using intent threshold: {intent_threshold}")

                return result['label'] if result['score'] > intent_threshold else "unknown"
        except AttributeError as e:
            logger.error(f"Missing setting in configuration: {str(e)}")
            return "unknown"
        except Exception as e:
            logger.error(f"Error in intent detection: {str(e)}")
            return "unknown" 

    # Use a custom-trained model for intent detection.
    def _custom_intent_detection(self, query: str) -> str:
        inputs = self.custom_intent_tokenizer(query, padding=True, truncation=True, return_tensors="pt")
        outputs = self.custom_intent_model(**inputs)
        probs = outputs.logits.softmax(dim=-1)
        predicted_class = torch.argmax(probs).item()
        confidence = probs[0][predicted_class].item()
        
        if confidence > settings.CUSTOM_INTENT_MODEL:
            return self.custom_intent_model.config.id2label[predicted_class]
        return "unknown"

    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        """
        Answer a question based on the given context.
        """
        try:
            result = self.qa_model(question=question, context=context)
            return {
                "answer": result['answer'],
                "confidence": result['score'],
                "start": result['start'],
                "end": result['end']
            }
        except Exception as e:
            logger.error(f"Error in question answering: {str(e)}")
            return {"answer": "", "confidence": 0.0, "start": -1, "end": -1}

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of the given text.
        """
        try:
            result = self.sentiment_analyzer(text)[0]
            return {
                "sentiment": result['label'],
                "confidence": result['score']
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0}

    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Generate a summary of the given text.
        """
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Error in text summarization: {str(e)}")
            return ""

    def rank_answers(self, query: str, answers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank the given answers based on their relevance to the query.
        """
        try:
            query_embedding = self.sentence_transformer.encode(query, convert_to_tensor=True)
            answer_embeddings = self.sentence_transformer.encode([a['content'] for a in answers], convert_to_tensor=True)
            
            cos_scores = util.pytorch_cos_sim(query_embedding, answer_embeddings)[0]
            top_results = torch.topk(cos_scores, k=min(len(answers), 10))
            
            ranked_answers = [
                {**answers[idx.item()], "relevance_score": score.item()}
                for score, idx in zip(top_results.values, top_results.indices)
            ]
            
            return sorted(ranked_answers, key=lambda x: x['relevance_score'], reverse=True)
        except Exception as e:
            logger.error(f"Error in answer ranking: {str(e)}")
            return answers

    # Extract the most important keywords from the given text.
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        try:
            # This is a simple implementation. For better results, consider using a dedicated keyword extraction library.
            words = text.lower().split()
            word_freq = {}
            for word in words:
                if word not in settings.STOPWORDS:
                    word_freq[word] = word_freq.get(word, 0) + 1
            return sorted(word_freq, key=word_freq.get, reverse=True)[:top_k]
        except Exception as e:
            logger.error(f"Error in keyword extraction: {str(e)}")
            return []

    def generate_response(self, query: str, context: str) -> str:
        """
        Generate a response based on the query and context.
        """
        try:
            # This is a placeholder. In a real-world scenario, you might use a more sophisticated
            # language generation model like GPT-3 or a fine-tuned model for your specific use case.
            answer = self.answer_question(context, query)
            return f"Based on the information provided, {answer['answer']}"
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}")
            return "I'm sorry, but I couldn't generate a response based on the given information."

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        """
        try:
            # This is a placeholder. You might want to use a dedicated language detection library
            # like langdetect or a pre-trained model for more accurate results.
            return "en"  # Assuming English for now
        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return "unknown"

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the semantic similarity between two texts.
        """
        try:
            embedding1 = self.sentence_transformer.encode(text1, convert_to_tensor=True)
            embedding2 = self.sentence_transformer.encode(text2, convert_to_tensor=True)
            return util.pytorch_cos_sim(embedding1, embedding2).item()
        except Exception as e:
            logger.error(f"Error in similarity calculation: {str(e)}")
            return 0.0

    # Classify the given text into one of the provided labels.
    def classify_text(self, text: str, labels: List[str]) -> Tuple[str, float]:
        try:
            text_embedding = self.sentence_transformer.encode(text, convert_to_tensor=True)
            label_embeddings = self.sentence_transformer.encode(labels, convert_to_tensor=True)
            
            similarities = util.pytorch_cos_sim(text_embedding, label_embeddings)[0]
            best_match_idx = similarities.argmax().item()

            print(f"Text: {text}")
            print(f"Labels: {labels}")
            print(f"Similarities: {similarities.tolist()}")
            
            return labels[best_match_idx], similarities[best_match_idx].item()
        except Exception as e:
            logger.error(f"Error in text classification: {str(e)}")
            return "unknown", 0.0

    # Extract entities from the given text using a named entity recognition model.
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        try:
            # Assuming a pre-trained NER model is available
            ner_model = pipeline("token-classification", model=settings.NER_MODEL, aggregation_strategy="simple")
            entities = ner_model(text)
            return [{"text": entity["word"], "start": entity["start"], "end": entity["end"], "type": entity["entity_group"]} for entity in entities]
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            return []

    # Generate text based on the given prompt using a language generation model.
    def generate_text(self, prompt: str, max_length: int = 50) -> str:
        try:
            generator = pipeline("text-generation", model=settings.NLP_MODEL)
            generated = generator(prompt, max_length=max_length, num_return_sequences=1)
            return generated[0]['generated_text']
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return "I'm sorry, but I couldn't generate text based on the prompt."

    # Process the input text to extract intent, entities, and sentiment.
    def process_text(self, text: str) -> Dict[str, Any]:
        try:
            intent = self.detect_intent(text)
            entities = self.extract_entities(text)
            sentiment = self.analyze_sentiment(text)
            keywords = self.extract_keywords(text)

            return {
                "intent": intent,
                "entities": entities,
                "sentiment": sentiment,
                "keywords": keywords
            }
        except Exception as e:
            logger.error(f"Error in processing text: {str(e)}")
            return {"intent": "unknown", "entities": [], "sentiment": {"sentiment": "neutral", "confidence": 0.0}, "keywords": []}

# Instantiate the NLPEngine
nlp_engine = NLPEngine()

