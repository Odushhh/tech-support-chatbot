import requests
import logging
from typing import List, Dict, Any
from github import Github
from stackapi import StackAPI
from backend.app.core import settings
from backend.app.utils.helpers import sanitize_html, truncate_text

logger = logging.getLogger(__name__)

class DataIntegration:
    def __init__(self):
        self.github_api = Github(settings.GITHUB_API_TOKEN)
        self.stackoverflow_api = StackAPI('stackoverflow', key=settings.STACKOVERFLOW_API_KEY)
        self.session = requests.Session()

    def fetch_stackoverflow_data(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch relevant data from StackOverflow based on the query.
        """
        try:
            questions = self.stackoverflow_api.fetch('search/advanced', 
                                                     q=query, 
                                                     sort='relevance', 
                                                     order='desc', 
                                                     accepted=True, 
                                                     pagesize=limit)
            
            results = []
            for question in questions['items']:
                answers = self.stackoverflow_api.fetch('questions/{}/answers'.format(question['question_id']), 
                                                       sort='votes', 
                                                       order='desc', 
                                                       pagesize=1, 
                                                       filter='withbody')
                
                if answers['items']:
                    answer = answers['items'][0]
                    sanitized_answer = sanitize_html(answer['body'])
                    truncated_answer = truncate_text(sanitized_answer, 500)
                    results.append({
                        'title': question['title'],
                        'question_url': question['link'],
                        'answer': truncated_answer,
                        'score': answer['score'],
                        'source': 'StackOverflow'
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error fetching StackOverflow data: {str(e)}")
            return []

    def fetch_github_issues(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch relevant issues from GitHub based on the query.
        """
        try:
            issues = self.github_api.search_issues(query=query, sort='reactions', order='desc')
            
            results = []
            for issue in issues[:limit]:
                sanitized_body = sanitize_html(issue.body)
                truncated_body = truncate_text(sanitized_body, 500)
                results.append({
                    'title': issue.title,
                    'url': issue.html_url,
                    'body': truncated_body,
                    'state': issue.state,
                    'comments': issue.comments,
                    'source': 'GitHub'
                })
            
            return results
        except Exception as e:
            logger.error(f"Error fetching GitHub issues: {str(e)}")
            return []

    def fetch_documentation(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch relevant documentation. This is a placeholder and should be 
        implemented based on your specific documentation sources.
        """
        # Placeholder implementation
        return [
            {
                'title': f'Documentation for {query}',
                'content': f'This is a placeholder for documentation about {query}.',
                'source': 'Internal Docs'
            }
        ]

    def fetch_troubleshooting_steps(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch troubleshooting steps. This is a placeholder and should be 
        implemented based on your specific troubleshooting data source.
        """
        # Placeholder implementation
        return [
            {
                'step': 1,
                'description': f'First step in troubleshooting {query}',
                'source': 'Internal Troubleshooting Guide'
            },
            {
                'step': 2,
                'description': f'Second step in troubleshooting {query}',
                'source': 'Internal Troubleshooting Guide'
            }
        ]

    def fetch_general_info(self, query: str) -> Dict[str, Any]:
        """
        Fetch general information. This is a placeholder and should be 
        implemented based on your specific general information source.
        """
        # Placeholder implementation
        return {
            'content': f'General information about {query}',
            'source': 'Internal Knowledge Base'
        }

    def update_stackoverflow_data(self):
        """
        Update local storage with latest StackOverflow data.
        This method should be implemented based on your specific storage mechanism.
        """
        # Placeholder implementation
        logger.info("Updating StackOverflow data in local storage")
        # Fetch and store data

    def update_github_issues(self):
        """
        Update local storage with latest GitHub issues.
        This method should be implemented based on your specific storage mechanism.
        """
        # Placeholder implementation
        logger.info("Updating GitHub issues in local storage")
        # Fetch and store data

    def update_documentation(self):
        """
        Update local documentation storage.
        This method should be implemented based on your specific documentation system.
        """
        # Placeholder implementation
        logger.info("Updating documentation in local storage")
        # Fetch and store updated documentation

    def search_stackoverflow(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search StackOverflow for relevant questions and answers.
        """
        return self.fetch_stackoverflow_data(query, limit)

    def search_github_issues(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search GitHub for relevant issues.
        """
        return self.fetch_github_issues(query, limit)

    def fetch_relevant_data(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch relevant data from all sources for a given query.
        """
        return {
            'stackoverflow': self.fetch_stackoverflow_data(query),
            'github': self.fetch_github_issues(query),
            'documentation': self.fetch_documentation(query),
            'troubleshooting': self.fetch_troubleshooting_steps(query),
            'general_info': self.fetch_general_info(query)
        }

