import logging
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, pipeline

load_dotenv()

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.nlp_model = AutoModelForSequenceClassification.from_pretrained(os.getenv("SENTIMENT_ANALYSIS_MODEL"))
        self.model = pipeline("text-classification", os.getenv("NLP_MODEL"))
        self.github_api_url = f"https://api.github.com/search/issues"
        self.stackoverflow_api_url = f"https://api.stackexchange.com/2.2/search"

    # Might not be necessary. Model is already initialised above 
    def _initialize_nlp_model(self):
        model_name = os.getenv("SENTIMENT_ANALYSIS_MODEL")
        return pipeline("sentiment-analysis", model=model_name)

    def fetch_stackoverflow_data(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        sanitized_query = self.sanitize_input(query)
        #url = f"https://api.stackexchange.com/2.2/search?order=desc&sort=activity&q={sanitized_query}&site=stackoverflow"
        url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=python&site=stackoverflow&pagesize=10"
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f"Error fetching StackOverflow data: {response.status_code} - {response.text}")
            return {"error": "Failed to fetch StackOverflow data", "status_code": response.status_code}

        data = response.json()
        if 'items' not in data or not data['items']:
            logger.warning("No items found in StackOverflow data.")
            return {"items": [], "total_count": 0}

        indexed_items = []
        for item in data['items'][:limit]:
            processed_item = {
                'question_id': item['question_id'],
                'title': item['title'],
                'link': item['link'],
		'creation_date': item['creation_date'],
		'tags': item['tags'],
                'score': item['score']
                # 'source': 'StackOverflow'
            }
            indexed_items.append(processed_item)
        return {"items": indexed_items, "total_count": len(indexed_items)}

    def fetch_github_issues(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        sanitized_query = self.sanitize_input(query)
        url = f"https://api.github.com/search/issues?q={sanitized_query}&sort=created&order=desc"
        headers = {"Authorization": f"token {os.getenv('GITHUB_API_TOKEN')}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error fetching GitHub issues: {response.status_code} - {response.text}")
            return {"error": "Failed to fetch GitHub issues", "status_code": response.status_code}

        data = response.json()
        indexed_items = []
        for item in data.get('items', [])[:limit]:
            processed_item = {
                'id': item['id'],
                'title': item['title'],
                'html_url': item['html_url'],
                'body': item['body'],
                'state': item.get('state', 'unknown'),
                'comments': item.get('comments', 0),
                'created_at': item.get('created_at', '1970-01-01T00:00:00Z'),
                'updated_at': item.get('updated_at', '1970-01-01T00:00:00Z')
                # 'source': 'GitHub'
            }
            indexed_items.append(processed_item)
        return {"issues": indexed_items, "total_count": data.get('total_count', 0)}

    def fetch_from_pretrained_model(self, input_data: str) -> Dict[str, Any]:
        result = self.model(input_data)
        return {
            "input": input_data,
            "output": result
        }

    def _process_stackoverflow_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': item['title'],
            'url': item['question_url'],
            'score': item['score'],
            'source': 'StackOverflow'
        }

    def _process_github_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': item['title'],
            'url': item['html_url'],
            'body': item['body'],
            'state': item['state'],
            'comments': item['comments'],
            'source': 'GitHub'
        }

    def sanitize_input(self, query: str) -> str:
        # Implement your sanitization logic here
        return query.strip()

data_fetcher = DataFetcher()
