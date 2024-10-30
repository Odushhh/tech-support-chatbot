import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self):
        # In-memory storage
        self.interactions = []
        self.feedback = []
        self.code_examples = []

    # Store a user interaction in memory.
    def store_interaction(self, query: str, response: str):
        interaction = {
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow()
        }
        self.interactions.append(interaction)
        logger.info(f"Stored interaction: {query}")

    # Store user feedback for a specific interaction.
    def store_feedback(self, query_id: str, rating: int, comment: Optional[str] = None):
        feedback = {
            "query_id": query_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.utcnow()
        }
        self.feedback.append(feedback)
        logger.info(f"Stored feedback for query ID: {query_id}")

    # Retrieve recent interactions from memory.
    def get_recent_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.interactions[-limit:]

    # Get popular topics based on recent interactions. 
    def get_popular_topics(self, days: int = 7, limit: int = 10) -> List[str]:
        start_date = datetime.utcnow() - timedelta(days=days)
        topic_count = {}
        for interaction in self.interactions:
            if interaction["timestamp"] >= start_date:
                topic_count[interaction["query"]] = topic_count.get(interaction["query"], 0) + 1
        sorted_topics = sorted(topic_count.items(), key=lambda item: item[1], reverse=True)
        return [topic for topic, _ in sorted_topics[:limit]]

    # Get usage statistics for the chatbot.
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        total_interactions = sum(1 for interaction in self.interactions if interaction["timestamp"] >= start_date)
        avg_rating = sum(feedback["rating"] for feedback in self.feedback if feedback["timestamp"] >= start_date) / max(1, len(self.feedback))
        return {
            "total_interactions": total_interactions,
            "average_rating": round(avg_rating, 2),
            "period_days": days
        }

    # Store a code example in memory.
    def store_code_example(self, language: str, query: str, code: str, source: str):
        example = {
            "language": language,
            "query": query,
            "code": code,
            "source": source,
            "timestamp": datetime.utcnow()
        }
        self.code_examples.append(example)
        logger.info(f"Stored code example for query: {query}")

    # Retrieve code examples from memory.
    def get_code_examples(self, query: str, language: str, limit: int = 5) -> List[Dict[str, Any]]:
        return [example for example in self.code_examples if query.lower() in example["query"].lower() and example["language"] == language][:limit]

    # Remove data older than the specified number of days.
    def cleanup_old_data(self, days: int = 90):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        self.interactions = [interaction for interaction in self.interactions if interaction["timestamp"] >= cutoff_date]
        self.feedback = [feedback for feedback in self.feedback if feedback["timestamp"] >= cutoff_date]
        self.code_examples = [example for example in self.code_examples if example["timestamp"] >= cutoff_date]
        logger.info(f"Cleaned up data older than {days} days")

# Instantiate the DataStorage class
data_storage = DataStorage()
