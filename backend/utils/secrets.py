import os
from dotenv import load_dotenv
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_secrets():

    env_path = Path(__file__).parent.parent.parent / '.env'
    logger.info(f"Looking for .env file at: {env_path}")
    
    if not env_path.exists():
        raise FileNotFoundError(
            f"No .env file found at {env_path}. Please create one with your API credentials."
        )
    
    load_dotenv(env_path)
    logger.info(".env file loaded")
    
    required_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    logger.info("All required environment variables found")

def get_reddit_credentials():
    """Get Reddit API credentials"""
    load_secrets()
    return {
        'client_id': os.getenv('REDDIT_CLIENT_ID'),
        'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
        'user_agent': os.getenv('REDDIT_USER_AGENT')
    }