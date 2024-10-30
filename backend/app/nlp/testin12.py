import os
import random
from transformers import pipeline

# Print all values in the .env file one at a time
print("Contents of .env file:")
for key, value in os.environ.items():
    print(f"{key}: {value}")
    input("Press Enter to continue...")  # This will pause after each item

class Testing12:
    def __init__(self):
        self.qa_pipeline = pipeline(model=os.getenv("NLP_MODEL"))
        # self.qa_pipeline = pipeline("question-answering", model=settings.QA_MODEL)

    def get_random_question_answer(self):
        questions = [
            "What is the capital of Kenya?",
            "What is the largest planet in our solar system?",
            "Who wrote 'To Kill a Mockingbird'?",
            "What is the boiling point of water?",
            "What is the currency of Japan?"
        ]
        question = random.choice(questions)
        context = "Kenya is a country in East Africa with coastline on the Indian Ocean. Its capital and largest city is Nairobi. " \
                  "Jupiter is the largest planet in our solar system. " \
                  "To Kill a Mockingbird was written by Harper Lee. " \
                  "The boiling point of water is 100 degrees Celsius at sea level. " \
                  "The currency of Japan is the Yen."
        
        answer = self.qa_pipeline(question=question, context=context)
        return question, answer['answer']

# Example usage
if __name__ == "__main__":
    testing12 = Testing12()
    question, answer = testing12.get_random_question_answer()
    print(f"Question: {question}\nAnswer: {answer}")
