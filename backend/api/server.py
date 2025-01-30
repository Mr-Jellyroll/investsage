from fastapi import FastAPI
from backend.api.interface import InvestSageAPI
from backend.api.models import AnalysisRequest

app = FastAPI()
api = InvestSageAPI()

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    return api.analyze(request)

@app.get("/symbols")
async def get_symbols():
    return api.get_available_symbols()

@app.get("/capabilities")
async def get_capabilities():
    return api.get_analysis_capabilities()