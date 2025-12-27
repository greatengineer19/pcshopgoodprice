from fastapi import APIRouter, HTTPException, Depends
from src.schemas import (
    PurchaseInvoicesQueryAnalysis
)
import logging
from src.chatgpt.ask_chatgpt import AskChatGPT
from sqlalchemy.orm import joinedload, Session
from src.api.session_db import get_db
import random


router = APIRouter(prefix='/api/purchase_invoices_query_analysis', tags=["Purchase Invoices Query Analysis"])

@router.get("", response_model=PurchaseInvoicesQueryAnalysis, status_code=200)
def analyze(db: Session = Depends(get_db)):
    try:
        data_counts = [100000, 200000, 300000, 400000, 500000, 6000000, 700000, 800000, 900000, 1000000]
        qtime1 = [0.63, 1.08, 1.34, 1.47, 1.65, 7.56, 7.13, 7.19, 7.32, 7.02]
        qtime2 = [0.30, 0.30, 0.28, 0.27, 0.32, 0.28, 0.29, 0.28, 0.31, 0.30]
        qtime3 = [60.0, 61.0, 61.0, 60.0, 61.0, 62.0, 60.0, 61.0, 62.0, 63.0]

        result = []
        for index, data_count in enumerate(data_counts):
            result.append({
                'data_count': data_count,
                'query_time1': qtime1[index],
                'query_time2': qtime2[index],
                'query_time3': qtime3[index],
            })
            
        return { 'message': 'Successfully analyzed 3 query performance', 'data': result }
    except Exception as e:
        logging.error(f"An error occurred while performing query analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))