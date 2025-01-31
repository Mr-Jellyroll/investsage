from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add the project root to the Python path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from backend.api.interface import InvestSageAPI
from backend.api.models import AnalysisRequest, AnalysisResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API
api = InvestSageAPI()

@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    try:
        return api.analyze(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symbols/search")
async def search_symbols(query: str):
    try:
        symbols = api.get_available_symbols()
        filtered = [s for s in symbols if query.upper() in s]
        return filtered
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/capabilities")
async def get_capabilities():
    try:
        return api.get_analysis_capabilities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)