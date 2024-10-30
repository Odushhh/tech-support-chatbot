import os
import pytest
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from backend.app.data.fetcher import DataFetcher

@pytest.fixture(scope="module")
def github_data():
    return [
        {
            "id": 1,
            "title": "Test GitHub Issue",
            "html_url": "https://api.github.com/search/issues",
            "body": "This is a test GitHub issue",
            "state": "open",
            "comments": 3,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    ]

@pytest.fixture(scope="module")
def stackoverflow_data():
    return [
        {
            "question_id": 1,
            "title": "How to use Python?",
            "link": "https://api.stackexchange.com/2.2/search?site=stackoverflow",
            "score": 5
        }
    ]

def test_fetch_github_data(github_data):
    with patch('backend.app.data.fetcher.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"items": github_data}
        mock_get.return_value.text = "Success"

        data_fetcher = DataFetcher()
        data = data_fetcher.fetch_github_issues("test")
        print("Fetched GitHub Data: ", data)

        assert data['issues'] == github_data, f"Expected {github_data}, but got {data['issues']}"

def test_fetch_stackoverflow_data(stackoverflow_data):
    with patch('backend.app.data.fetcher.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"items": stackoverflow_data}
        mock_get.return_value.text = "Success"

        data_fetcher = DataFetcher()
        data = data_fetcher.fetch_stackoverflow_data("test")
        print("Fetched StackOverflow Data: ", data)
        assert data['items'] == stackoverflow_data, f"Expected {stackoverflow_data}, but got {data['items']}"

def test_model_prediction(github_data):
    data_fetcher = DataFetcher()
    input_data = github_data[0]['body']

    result = data_fetcher.fetch_from_pretrained_model(input_data)

    assert "input" in result
    assert "output" in result
    assert isinstance(result['output'], list), f"Expected a list of classifications, got {type(result['output'])}"
