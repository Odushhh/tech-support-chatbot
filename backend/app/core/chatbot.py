import logging
from typing import List, Tuple
from backend.app.nlp.engine import NLPEngine
from backend.app.data.integration import DataIntegration
from backend.app.data.storage import DataStorage, data_storage
from backend.app.data.fetcher import data_fetcher, DataFetcher
from backend.app.utils.helpers import sanitize_input, format_code_snippet

class TechSupportChatbot:
    def __init__(self):
        self.nlp_engine = NLPEngine()
        self.data_integration = DataIntegration()
        self.data_storage = DataStorage()
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = DataFetcher()

    # Main entry point 
    # Detects intent & routes user's query to the appropriate handler
    def process_query(self, query: str) -> Tuple[str, float, List[str]]:
        all_data = data_fetcher.fetch_all_data(query)
        #TODO:
        all_relevant_data = self.data_integration.fetch_relevant_data(all_data)
        # all_relevant_data = self.data_integration.fetch_relevant_data(query.text)
        
        # stackoverflow_results = data_integration.fetch_stackoverflow_data(query.text)
        # github_issues = data_integration.fetch_github_issues(query.text)
        
        """
        Process a user query and return a response.
        
        :param query: The user's input query
        :return: A tuple containing (response, confidence, sources)
        """
        try:
            sanitized_query = sanitize_input(query)
            intent = self.nlp_engine.detect_intent(sanitized_query)
            
            if intent == "bug_resolution":
                return self.handle_bug_resolution(sanitized_query)
            elif intent == "usage_guidance":
                return self.handle_usage_guidance(sanitized_query)
            elif intent == "troubleshooting":
                return self.handle_troubleshooting(sanitized_query)
            else:
                return self.handle_general_query(sanitized_query)
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return "I'm sorry, I encountered an error while processing your query. Please try again.", 0.0, []
        
        
        return response, confidence, sources

    def handle_bug_resolution(self, query: str) -> Tuple[str, float, List[str]]:
        """Handle queries related to bug resolution."""
        stackoverflow_data = self.data_integration.fetch_stackoverflow_data(query)
        github_issues = self.data_integration.fetch_github_issues(query)
        
        combined_data = stackoverflow_data + github_issues
        relevant_answers = self.nlp_engine.rank_answers(query, combined_data)
        
        if relevant_answers:
            best_answer = relevant_answers[0]
            response = f"Here's a possible solution to your bug:\n\n{best_answer['content']}"
            if 'code' in best_answer:
                response += f"\n\nHere's a code snippet that might help:\n{format_code_snippet(best_answer['code'])}"
            return response, best_answer['confidence'], best_answer['sources']
        else:
            return "I'm sorry, I couldn't find a specific solution to your bug. Can you provide more details?", 0.5, []

    def handle_usage_guidance(self, query: str) -> Tuple[str, float, List[str]]:
        """Handle queries related to usage guidance."""
        documentation = self.data_integration.fetch_documentation(query)
        relevant_sections = self.nlp_engine.extract_relevant_sections(query, documentation)
        
        if relevant_sections:
            response = "Here's some guidance on how to use this feature:\n\n"
            response += "\n".join(relevant_sections[:3])  # Limit to top 3 sections
            return response, 0.8, [doc['source'] for doc in documentation[:3]]
        else:
            return "I'm sorry, I couldn't find specific usage guidance for your query. Could you rephrase or provide more context?", 0.5, []

    def handle_troubleshooting(self, query: str) -> Tuple[str, float, List[str]]:
        """Handle queries related to troubleshooting."""
        troubleshooting_steps = self.data_integration.fetch_troubleshooting_steps(query)
        relevant_steps = self.nlp_engine.rank_troubleshooting_steps(query, troubleshooting_steps)
        
        if relevant_steps:
            response = "Here are some troubleshooting steps you can try:\n\n"
            for i, step in enumerate(relevant_steps[:5], 1):
                response += f"{i}. {step['content']}\n"
            return response, 0.7, [step['source'] for step in relevant_steps[:5]]
        else:
            return "I'm sorry, I couldn't find specific troubleshooting steps for your issue. Can you provide more details about the problem?", 0.5, []

    def handle_general_query(self, query: str) -> Tuple[str, float, List[str]]:
        """Handle general queries that don't fit into specific categories."""
        general_info = self.data_integration.fetch_general_info(query)
        relevant_info = self.nlp_engine.extract_relevant_info(query, general_info)
        
        if relevant_info:
            response = f"Here's some information that might help:\n\n{relevant_info['content']}"
            return response, 0.6, [relevant_info['source']]
        else:
            return "I'm not sure I understand your query. Could you please rephrase it or provide more context?", 0.3, []

    # Refresh KB from various data sources & Retrain the NLP model
    def update_knowledge_base(self):
        """Update the chatbot's knowledge base with fresh data."""
        try:
            self.data_integration.update_stackoverflow_data()
            self.data_integration.update_github_issues()
            self.data_integration.update_documentation()
            self.nlp_engine.retrain_model(self.data_storage.get_recent_interactions())
            return True
        except Exception as e:
            self.logger.error(f"Error updating knowledge base: {str(e)}")
            return False

    # Search for relevant issues across various platforms
    def search_issues(self, query: str, platform: str = "all", limit: int = 10) -> List[dict]:
        """
        Search for issues across specified platforms.
        
        :param query: The search query
        :param platform: The platform to search (stackoverflow, github, or all)
        :param limit: The maximum number of results to return
        :return: A list of relevant issues
        """
        results = []
        if platform in ["all", "stackoverflow"]:
            stackoverflow_results = self.data_integration.search_stackoverflow(query, limit)
            results.extend(stackoverflow_results)
        if platform in ["all", "github"]:
            github_results = self.data_integration.search_github_issues(query, limit)
            results.extend(github_results)
        
        return self.nlp_engine.rank_search_results(query, results)[:limit]

    # Generate potential solution based on user's query
    def suggest_solution(self, query: str) -> dict:
        """
        Suggest a solution based on the user's query.
        
        :param query: The user's query
        :return: A dictionary containing the suggested solution and its confidence score
        """
        relevant_data = self.data_integration.fetch_relevant_data(query)
        solution = self.nlp_engine.generate_solution(query, relevant_data)
        return {
            "solution": solution['content'],
            "confidence": solution['confidence'],
            "sources": solution['sources']
        }

    def log_interaction(self, query: str, response: str):
        """Log the interaction for future analysis and improvement."""
        self.data_storage.store_interaction(query, response)

    def get_popular_topics(self) -> List[str]:
        """Retrieve popular topics based on recent interactions."""
        popular_topics = data_storage.get_popular_topics()
        return self.data_storage.get_popular_topics()

    def get_usage_stats(self) -> dict:
        """Retrieve usage statistics of the chatbot."""
        return self.data_storage.get_usage_stats()

