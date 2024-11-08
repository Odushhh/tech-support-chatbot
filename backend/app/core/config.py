import os
from pydantic import Field, BaseModel, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Application Settings
    APP_NAME: str = Field("Tech Support Chatbot")
    APP_VERSION: str = Field("Version 1.0.0")
    APP_DESCRIPTION: str = Field("Chatbot leverages data from GitHub Issues & StackOverflow to provide assistance on software-related issues, troubleshooting steps, and overall programming guidance.")
    DEBUG: bool = Field(default=False, json_schema_extra={"env":"DEBUG"})
    ENVIRONMENT: str = Field("Development")

    # API Settings
    # API_V1_STR: str = "/api/v1"
    # API_KEY: str = Field("API_KEY")

    # Server Settings
    HOST: Optional[str] = Field("HOST")
    PORT: Optional[int] = Field("PORT")

    '''
    # Database Settings
    MONGODB_URL: str = Field(default=os.getenv("MONGODB_URL"), json_schema_extra={"env":"MONGODB_URL"})
    MONGODB_DB_NAME: str = Field(default=os.getenv("MONGODB_DB_NAME"), json_schema_extra={"env":"MONGODB_DB_NAME"})
    MONGODB_COLLECTION_NAME: str = Field(default=os.getenv("MONGODB_COLLECTION_NAME"), json_schema_extra={"env": "MONGODB_COLLECTION_NAME"})
    
    # Elasticsearch Settings
    ELASTICSEARCH_URL: str = Field(default=os.getenv("ELASTICSEARCH_URL"), json_schema_extra={"env": "ELASTICSEARCH_URL"})
    ELASTICSEARCH_API_KEY: str = Field(default=os.getenv("ELASTICSEARCH_API_KEY"), json_schema_extra={"env": "ELASTICSEARCH_API_KEY"})   
    ELASTICSEARCH_INDEX: str = Field(default=os.getenv("ELASTICSEARCH_INDEX"), json_schema_extra={"env": "ELASTICSEARCH_INDEX"})

    # Redis Settings (for caching)
    # REDIS_URL: str = Field(default=os.getenv(""), env="REDIS_URL")
    REDIS_TTL: int = Field(default=os.getenv("REDIS_TTL"), json_schema_extra={"env":"REDIS_TTL"}) # Time-to-live for cached items (in seconds)
    '''
    
    

    

    # NLP Model Settings
    NLP_MODEL_PATH: str = Field(default=os.getenv("NLP_MODEL_PATH"), json_schema_extra={"env":"NLP_MODEL_PATH"})

    INTENT_CLASSIFIER: str = Field(default=os.getenv("INTENT_CLASSIFICATION_MODEL"), json_schema_extra={"env":"INTENT_CLASSIFICATION_MODEL"})
    INTENT_CLASSIFICATION_THRESHOLD: float = Field(default=os.getenv("INTENT_CLASSIFICATION_THRESHOLD"), json_schema_extra={"env":"INTENT_CLASSIFICATION_THRESHOLD"})
    CUSTOM_INTENT_MODEL: str = Field(default=os.getenv("CUSTOM_INTENT_MODEL"), json_schema_extra={"env":"CUSTOM_INTENT_MODEL"})

    FEATURE_EXTRACTION_MODEL: str = Field(default=os.getenv("FEATURE_EXTRACTION_MODEL"), json_schema_extra={"env":"FEATURE_EXTRACTION_MODEL"})
    TOKENIZER: str = Field(default=os.getenv("TOKENIZER"), json_schema_extra={"env":"TOKENIZER"})
    NER_MODEL: str = Field(default=os.getenv("NER_MODEL"), json_schema_extra={"env":"NER_MODEL"})  
    STOPWORDS: str = Field(default=os.getenv("STOPWORDS"), json_schema_extra={"env:": "STOPWORDS"})
    
    SUMMARIZATION_MODEL: str = Field(default=os.getenv("SUMMARIZATION_MODEL"), json_schema_extra={"env":"SUMMARIZATION_MODEL"})
    SENTENCE_TRANSFORMER_MODEL: str = Field(default=os.getenv("SENTENCE_TRANSFORMER_MODEL"), json_schema_extra={"env":"SENTENCE_TRANSFORMER_MODEL"})
    SENTIMENT_ANALYSIS_MODEL: str = Field(default=os.getenv("SENTIMENT_ANALYSIS_MODEL"), json_schema_extra={"env":"SENTIMENT_ANALYSIS_MODEL"})
    QA_MODEL: str = Field(default=os.getenv("QA_MODEL"), json_schema_extra={"env":"QA_MODEL"})

    # Data Integration Settings
    HUGGINGFACE_API_TOKEN: str = Field(default=os.getenv("HUGGINGFACE_API_TOKEN"), json_schema_extra={"env":"HUGGINGFACE_API_TOKEN"})
    STACKOVERFLOW_API_KEY: str = Field(default=os.getenv("STACKOVERFLOW_API_KEY"), json_schema_extra={"env":"STACKOVERFLOW_API_KEY"})
    GITHUB_API_TOKEN: str = Field(default=os.getenv("GITHUB_API_TOKEN"), json_schema_extra={"env":"GITHUB_API_TOKEN"})
    MAX_RESULTS_PER_QUERY: int = Field(default=os.getenv("MAX_RESULTS_PER_QUERY"), json_schema_extra={"env":"MAX_RESULTS_PER_QUERY"})

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=os.getenv("RATE_LIMIT_REQUESTS"), json_schema_extra={"env":"RATE_LIMIT_REQUESTS"})
    RATE_LIMIT_PERIOD: int = Field(default=os.getenv("RATE_LIMIT_PERIOD"), json_schema_extra={"env":"RATE_LIMIT_PERIOD"})  # Period in seconds

    # Logging
    LOG_DIR: str = Field(default=os.getenv("LOG_DIR"), json_schema_extra={"env":"/home/adrian-oduma/Desktop/Projects/ts-chatbot-v2/backend/app"}        # Ubuntu file path
    LOG_DIR: str = Field(default=os.getenv("LOG_DIR"), json_schema_extra={"env":"/home/adrian-oduma/Desktop/Projects/ts-chatbot-v2/backend/app"}        # Windows file path

    LOG_LEVEL: str = Field(default=os.getenv("LOG_LEVEL"), json_schema_extra={"env":"LOG_LEVEL"})
    LOG_FILE_PATH: Optional[str] = Field(default=os.getenv("LOG_FILE_PATH"), json_schema_extra={"env":"LOG_FILE_PATH"})

    # Security
    SECRET_KEY: str = Field(default=os.getenv(""), env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], json_schema_extra={"env": ["ALLOWED_HOSTS"]})
    CORS_ORIGINS: List[str] = Field(default=["*"], json_schema_extra={"env": ["CORS_ORIGINS"]})

    @field_validator("ALLOWED_HOSTS", "CORS_ORIGINS", mode="before")
    def parse_comma_separated_strings(cls, v):
        # If value is a string, split by commas
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v


    model_config = ConfigDict(env_file=".env")

    # Chatbot Behavior
    MAX_CONVERSATION_HISTORY: int = Field(default=os.getenv("MAX_CONVERSATION_HISTORY"), json_schema_extra={"env":"MAX_CONVERSATION_HISTORY"})
    CONFIDENCE_THRESHOLD: float = Field(default=os.getenv("CONFIDENCE_THRESHOLD"), json_schema_extra={"env":"CONFIDENCE_THRESHOLD"})
    MAX_RESPONSE_LENGTH: int = Field(default=os.getenv("MAX_RESPONSE_LENGTH"), json_schema_extra={"env":"MAX_RESPONSE_LENGTH"})

    # Feature Flags
    ENABLE_SPELL_CHECK: bool = Field(default=os.getenv("ENABLE_SPELL_CHECK"), json_schema_extra={"env":"ENABLE_SPELL_CHECK"})
    ENABLE_SENTIMENT_ANALYSIS: bool = Field(default=os.getenv("ENABLE_SENTIMENT_ANALYSIS"), json_schema_extra={"env":"ENABLE_SENTIMENT_ANALYSIS"})
    ENABLE_MULTILINGUAL_SUPPORT: bool = Field(default=os.getenv("ENABLE_MULTILINGUAL_SUPPORT"), json_schema_extra={"env":"ENABLE_MULTILINGUAL_SUPPORT"})

    # External Services
    # SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    # SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")

    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING: bool = Field(default=os.getenv("ENABLE_PERFORMANCE_MONITORING"), json_schema_extra={"env":"ENABLE_PERFORMANCE_MONITORING"})
    PERFORMANCE_MONITORING_INTERVAL: int = Field(default=os.getenv("PERFORMANCE_MONITORING_INTERVAL"), json_schema_extra={"env":"PERFORMANCE_MONITORING_INTERVAL"})  # In seconds

    # Data Retention Policy
    DATA_RETENTION_DAYS: int = Field(default=os.getenv("DATA_RETENTION_DAYS"), json_schema_extra={"env":"DATA_RETENTION_DAYS"})

    # Feedback System
    MIN_FEEDBACK_SCORE: int = Field(default=os.getenv("MIN_FEEDBACK_SCORE"), json_schema_extra={"env":"MIN_FEEDBACK_SCORE"})
    MAX_FEEDBACK_SCORE: int = Field(default=os.getenv("MAX_FEEDBACK_SCORE   "), json_schema_extra={"env":"MAX_FEEDBACK_SCORE"})

    
    

    '''
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    '''

    @property
    def fastapi_kwargs(self):
        return {
            "debug": self.DEBUG,
            "title": self.APP_NAME,
            "version": self.APP_VERSION,
        }

settings = Settings(host="localhost", port=8080, DEBUG=True)

'''
def get_settings():
    return Settings()

# Instantiate settings
settings = get_settings()

'''
