import os
import sys
from unittest.mock import patch, MagicMock

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
		    "id": 1981998226,
                    "title": "🚩 add flag to only install riscv if user wants",
                    "html_url": "https://github.com/esp-rs/espup/pull/391",
                    "body": "null",
                    "state": "closed",
                    "comments": 7,
                    "created_at": "2023-11-07T18:42:08Z",
                    "updated_at": "2024-01-02T00:00:25Z"
                }
            ],
	    "total_count": 1
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
		    "question_id": 231767,
                    "title": "What does the &quot;yield&quot; keyword do in Python?",
                    "link": "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python",
                    "creation_date": "1224800471",
                    "tags": ["python", "iterator", "generator", "yield"],
                    "score": 13008
                }
            ]
        }
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def data_fetcher():
    return DataFetcher()

# Testing the GitHub API connection
@patch('requests.get')
def test_fetch_github_issues(mock_get, data_fetcher):

    # Sample data
    mock_response = {
	"items": [
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
	],
	"total_count": 1
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    github_query = "test"
    # mock_api_response('github')
    github_data = data_fetcher.fetch_github_issues(github_query)
    print("GitHub data fetched:", github_data)

    # Assertions to check if the returned data is accurate
    assert "issues" in github_data, "Expected 'issues' key not found in GitHub data."
    github_issues = github_data["issues"]

    assert len(github_data) > 0
    first_item = github_issues[0]
    assert "id" in first_item, "Missing 'title' key in the first item" # github_data[0]
    assert "title" in first_item, "Missing 'title' key in the first item" #github_data[0]
    assert "html_url" in first_item, "Missing 'title' key in the first item" # github_data[0]
    assert "body" in first_item, "Missing 'title' key in the first item" #github_data[0]
    assert "state" in first_item, "Missing 'title' key in the first item" # github_data[0]
    assert "comments" in  first_item, "Missing 'title' key in the first item"  #github_data[0]
    assert "created_at" in first_item, "Missing 'title' key in the first item" # github_data[0]
    assert "updated_at" in first_item, "Missing 'title' key in the first item" # github_data[0]

    # Verify the GitHub API call
    mock_get.assert_called_once_with(
	f"https://api.github.com/search/issues?q={github_query}&sort=created&order=desc", 
	headers={"Authorization": f"token {GITHUB_API_TOKEN}"})

    '''
    # Process the fetched data using the Hugging Face model
    for item in github_data:
        sentiment_result = data_fetcher.fetch_from_pretrained_model(item['body'])
        assert "input" in sentiment_result
        assert "output" in sentiment_result

    print("GitHub API integration test passed successfully!")
    '''
# Testing the StackOverflow API connection
@patch('requests.get')
def test_fetch_stackoverflow_data(mock_get, data_fetcher):

    # Sample data
    mock_response = {
	"items": [
	    {
		"question_id": 231767,
		"title": "What does the &quot;yield&quot; keyword do in Python?",
		"link": "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python",
		"creation_date": "1224800471",
		"tags": ["python", "iterator", "generator", "yield"],
		"score": 13007
	    }
	],
	"total_count": 1
    }

    # MagicMock object for mocked functions
    #mock_fetch_from_stackoverflow_api = MagicMock()
    #data_fetcher.fetch_from_stackoverflow_api =  mock_fetch_from_stackoverflow_api

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    stackoverflow_query = "test"
    # mock_api_response('stackoverflow')
    stackoverflow_data = data_fetcher.fetch_stackoverflow_data(stackoverflow_query)

    print("StackOverflow data fetched: ", stackoverflow_data)

    # Assertions to check if the returned data is accurate
    assert "items" in stackoverflow_data, "Expected 'items' key not found in StackOverflow data."
    stackoverflow_items = stackoverflow_data["items"]

    assert len(stackoverflow_data) > 0
    first_item = stackoverflow_items[0]
    assert "question_id" in first_item
    assert "title" in first_item, "Missing 'title' key in the first item"
    assert "link" in first_item, "Missing 'title' key in the first item"  #stackoverflow_data
    assert "creation_date" in first_item, "Missing 'title' key in the first item"  #stackoverflow_data
    assert "tags" in first_item, "Missing 'title' key in the first item" #stackoverflow_data
    assert "score" in first_item, "Missing 'title' key in the first item" #stackoverflow_data

    # Verify Stack Overflow API call
    mock_get.assert_called_once_with(
        "https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=python&site=stackoverflow&pagesize=10") 



    '''
    # Process the fetched data using the Hugging Face model
    for item in stackoverflow_data:
        sentiment_result = data_fetcher.fetch_from_pretrained_model(item['title'])
        assert "input" in sentiment_result
        assert "output" in sentiment_result

    print("StackOverflow API integration test passed successfully!")


def test_api_integration(mock_github_api, mock_stackoverflow_api):
    # Initialize DataFetcher
    data_fetcher = DataFetcher()

    # Test GitHub API
    github_query = "test"
    github_data = data_fetcher.fetch_github_issues(github_query)["issues"]
    assert len(github_data) > 0
    assert "id" in github_data[0]
    assert "title" in github_data[0]
    assert "body" in github_data[0]
    assert "html_url" in github_data[0]
    assert "state" in  github_data[0]
    assert "comments" in github_data[0]
    assert "created_at" in github_data[0]
    assert "updated_at" in github_data[0]

    # Verify GitHub API call
    mock_github_api.assert_called_once_with(
        f"https://api.github.com/search/issues?q={github_query}&sort=created&order=desc",
        headers={"Authorization": f"token {GITHUB_API_TOKEN}"}
    )

    # Test Stack Overflow API
    stackoverflow_query = "python test"
    stackoverflow_data = data_fetcher.fetch_stackoverflow_data(stackoverflow_query)["items"]
    assert len(stackoverflow_data) > 0
    assert "question_id" in stackoverflow_data[0]
    assert "title" in stackoverflow_data[0]
    assert "link" in stackoverflow_data[0]
    assert "creation_date" in stackoverflow_data[0]
    assert "tags" in stackoverflow_data[0]

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

    print("All API integration tests passed successfully!")


    # Process the fetched data using the Hugging Face model
    for item in stackoverflow_data:
        sentiment_result = data_fetcher.fetch_from_pretrained_model(item['title'])
        assert "input" in sentiment_result
        assert "output" in sentiment_result

    print("All API integration tests passed successfully!")
    '''

if __name__ == "__main__":
    pytest.main([__file__])
