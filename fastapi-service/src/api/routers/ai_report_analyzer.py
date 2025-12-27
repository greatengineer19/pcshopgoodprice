from fastapi import APIRouter, HTTPException
from src.schemas import (
    ReportAnalyzerParams,
    ReportAnalyzerResponse
)
import logging
from src.chatgpt.ask_chatgpt import AskChatGPT


router = APIRouter(prefix='/api/chatbot/analyze_report', tags=["Report Analyzer"])

@router.post("", response_model=ReportAnalyzerResponse, status_code=200)
def analyze_report(params: ReportAnalyzerParams):
    try:
        user_input = params.user_input
        response_from_chatgpt = AskChatGPT.build_response(user_input)

        return { 'chatgpt_response': response_from_chatgpt }
    except Exception as e:
        logging.error(f"An error occurred while in analyze report: {e}")
        raise HTTPException(status_code=500, detail=str(e))