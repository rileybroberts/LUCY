"""
Configuration settings for LUCY - 1978 Triumph Spitfire RAG System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress ChromaDB telemetry and warnings to clean up output
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# Suppress specific warnings for cleaner output
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*telemetry.*")

class SpitfireConfig:
    """Configuration settings for the Spitfire RAG system"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Configuration
    LLM_MODEL = "claude-3-5-sonnet-20241022"  # Latest Claude Sonnet
    EMBEDDING_MODEL = "text-embedding-3-large"
    
    # File Paths
    DOCS_DIR = "./data/docs"
    VECTORDB_DIR = "./data/vectordb"
    MAINTENANCE_LOG_PATH = "./data/maintenance_log.json"
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RETRIEVAL = 4
    
    # Memory Configuration
    CONVERSATION_MEMORY_SIZE = 15  # Remember last 15 exchanges
    
    # Vector Database
    COLLECTION_NAME = "lucy_spitfire_docs"
    
    # LUCY's Details
    LUCY_YEAR = 1978
    LUCY_MODEL = "Triumph Spitfire 1500"
    LUCY_ENGINE = "1.5L inline-4"
    LUCY_AGE = 2025 - LUCY_YEAR  # Currently 47 years old
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not cls.ANTHROPIC_API_KEY:
            missing_keys.append("ANTHROPIC_API_KEY")
        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
            
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True