from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..models.email import (
    EmailDetail, SendEmailRequest, DraftEmailRequest,
    AutoReplyRequest, GenerateSummaryRequest, GenerateSummaryResponse
)
from ..services.gmail_service import (
    fetch_emails, fetch_email_content, send_email, create_draft, get_email_body
)
from ..services.gpt_service import generate_auto_reply, generate_summary
from ..dependencies.dependencies import get_gmail_service_dependency

router = APIRouter()

@router.get("/", response_model=List[EmailDetail])
def list_emails(service=Depends(get_gmail_service_dependency), max_results: int = 10):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    return fetch_emails(service, max_results=max_results)

@router.get("/{email_id}", response_model=EmailDetail)
def get_email(email_id: str, service=Depends(get_gmail_service_dependency)):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    email = fetch_email_content(service, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/send", response_model=dict)
def send_email_route(request: SendEmailRequest, service=Depends(get_gmail_service_dependency)):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    result = send_email(service, request.to, request.subject, request.body, threadId=request.threadId)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return result

@router.post("/draft", response_model=dict)
def draft_email(request: DraftEmailRequest, service=Depends(get_gmail_service_dependency)):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    result = create_draft(service, request.to, request.subject, request.body, threadId=request.threadId)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create draft")
    return result

@router.post("/{email_id}/auto-reply", response_model=dict)
def generate_auto_reply_route(email_id: str, request: AutoReplyRequest, service=Depends(get_gmail_service_dependency)):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    email = fetch_email_content(service, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email_body = get_email_body(email.payload)
    reply = generate_auto_reply(email_body, request.additional_instructions)
    return {"reply": reply}

@router.post("/{email_id}/summary", response_model=GenerateSummaryResponse)
def summarize_email(email_id: str, request: GenerateSummaryRequest, service=Depends(get_gmail_service_dependency)):
    if not service:
        raise HTTPException(status_code=500, detail="Gmail service unavailable")
    email = fetch_email_content(service, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email_body = get_email_body(email.payload)
    summary = generate_summary(email_body, request.additional_instructions)
    return GenerateSummaryResponse(email_id=email.id, summary=summary)
