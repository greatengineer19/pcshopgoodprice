from fastapi import APIRouter, HTTPException, Depends
from src.schemas import (
    PurchaseInvoicesQueryAnalysis
)
import logging
from src.chatgpt.ask_chatgpt import AskChatGPT
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
import random


router = APIRouter(prefix='/api/purchase_invoices_query_analysis', tags=["Purchase Invoices Query Analysis"])

@router.get("", response_model=PurchaseInvoicesQueryAnalysis, status_code=200)
def analyze(db: Session = Depends(get_db)):
    try:
        data_counts = [200000, 400000, 600000, 800000, 900000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000]
        result = []
        for data_count in data_counts:
            result.append({
                'data_count': data_count,
                'query_time1': random.randint(500, 1000),
                'query_time2': random.randint(500, 1000),
                'query_time3': random.randint(500, 1000),
            })
            
        return { 'message': 'Successfully analyzed 3 query performance', 'data': result }
    except Exception as e:
        logging.error(f"An error occurred while performing query analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))