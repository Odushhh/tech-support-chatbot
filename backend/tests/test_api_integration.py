import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.app.data.fetcher import DataFetcher

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
print(f"Project root: {project_root}")

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
STACKOVERFLOW_API_KEY = os.getenv("STACKOVERFLOW_API_KEY")

@pytest.fixture
def mock_github_api():
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 1,
                    "title": "Test GitHub Issue",
                    "body": "This is a test GitHub issue",
                    "html_url": "https://github.com/test/repo/issues/1",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                }
            ]
        }
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_stackoverflow_api():
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "question_id": 1,
                    "title": "Test Stack Overflow Question",
                    "link": "https://stackoverflow.com/questions/1",
                    "creation_date": 1672531200,
                    "tags": ["python", "testing"],
                }
            ]
        }
        mock_get.return_value = mock_response
        yield mock_get

def test_api_integration(mock_github_api, mock_stackoverflow_api):
    # Initialize DataFetcher
    data_fetcher = DataFetcher()

    # Test GitHub API
    github_query = "test"
    github_data = data_fetcher.fetch_github_issues(github_query)
    assert len(github_data) > 0
    assert "id" in github_data[0]
    assert "title" in github_data[0]
    assert "body" in github_data[0]
    assert "html_url" in github_data[0]

    # Verify GitHub API call
    mock_github_api.assert_called_once_with(
        f"https://api.github.com/search/issues?q={github_query}&sort=created&order=desc",
        headers={"Authorization": f"token {GITHUB_API_TOKEN}"}
    )

    # Test Stack Overflow API
    stackoverflow_query = "python test"
    stackoverflow_data = data_fetcher.fetch_stackoverflow_data(stackoverflow_query)
    assert len(stackoverflow_data) > 0
    assert "question_id" in stackoverflow_data[0]
    assert "title" in stackoverflow_data[0]
    assert "link" in stackoverflow_data[0]

    # Verify Stack Overflow API call
    mock_stackoverflow_api.assert_called_once_with(
        "https://api.stackexchange.com/2.2/search/advanced",
        params={
            "order": "desc",
            "sort": "activity",
            "q": stackoverflow_query,
            "site": "stackoverflow",
            "key": STACKOVERFLOW_API_KEY
        }
    )

    # Process the fetched data using the Hugging Face model
    for item in github_data:
        sentiment_result = data_fetcher.fetch_from_pretrained_model(item['body'])
        assert "input" in sentiment_result
        assert "output" in sentiment_result

    for item in stackoverflow_data:
        sentiment_result = data_fetcher.fetch_from_pretrained_model(item['title'])
        assert "input" in sentiment_result
        assert "output" in sentiment_result

    print("All API integration tests passed successfully!")

if __name__ == "__main__":
    pytest.main([__file__])