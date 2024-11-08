import os
import pytest
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from backend.app.data.fetcher import DataFetcher

@pytest.fixture(scope="module")
def github_data():
    return [
        {
	    "id": 1981998226,
            "title": "🚩 add flag to only install riscv if user wants",
            "html_url": "https://github.com/esp-rs/espup/pull/391",
            "body": "null",
            "state": "closed",
            "comments": 7,
            "created_at": "2023-11-07T18:42:08Z",
            "updated_at": "2024-01-02T00:00:25Z"
        }
    ]

@pytest.fixture(scope="module")
def stackoverflow_data():
    return [
        {
            "question_id": 231767,
	    "title": "What does the &quot;yield&quot; keyword do in Python?",
            "link": "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python",
            "creation_date": "1224800471",
            "tags": ["python", "iterator", "generator", "yield"],
            "score": 13007
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
