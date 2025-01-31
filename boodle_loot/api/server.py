from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from .models import AnalysisRequest, AnalysisResponse
from .interface import InvestSageAPI

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API
api = InvestSageAPI()

@app.get("/stock/search")
async def search_symbols(q: str = Query(..., description="Search query")) -> List[str]:
    try:
        # Mock data for testing
        mock_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'BAC', 'WMT'
        ]
        
        # Convert query to uppercase for case-insensitive search
        search_query = q.upper()
        logger.info(f"Searching for symbols matching: {search_query}")
        
        # Filter symbols that match the search query
        filtered = [symbol for symbol in mock_symbols if search_query in symbol]
        logger.info(f"Found {len(filtered)} matching symbols: {filtered}")
        
        return filtered
        
    except Exception as e:
        logger.error(f"Error in symbol search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    try:
        logger.info(f"Fetching stock data for symbol: {symbol}")
        return {
            "symbol": symbol,
            "price": 100.00,
            "change": 2.50,
            "changePercent": 2.5,
            "volume": 1000000,
            "previousClose": 97.50
        }
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    try:
        logger.info(f"Analyzing {request.analysis_type} for symbol: {request.symbol}")
        result = api.analyze(request)
        return AnalysisResponse(
            success=True,
            data=result.data if hasattr(result, 'data') else result,
            metadata={"timestamp": result.metadata.get("timestamp") if hasattr(result, 'metadata') else None}
        )
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )