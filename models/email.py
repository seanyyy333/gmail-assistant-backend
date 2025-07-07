from pydantic import BaseModel
from typing import List, Optional, Any

class MessagePartHeader(BaseModel):
    name: str
    value: str

class MessagePartBody(BaseModel):
    size: int
    data: Optional[str] = None

class MessagePart(BaseModel):
    partId: Optional[str] = None
    mimeType: str
    filename: Optional[str] = None
    headers: Optional[List[MessagePartHeader]] = None
    body: MessagePartBody
    parts: Optional[List['MessagePart']] = None

MessagePart.model_rebuild()

class MessagePayload(BaseModel):
    partId: Optional[str] = None
    mimeType: str
    filename: Optional[str] = None
    headers: Optional[List[MessagePartHeader]] = None
    body: MessagePartBody
    parts: Optional[List[MessagePart]] = None

class EmailDetail(BaseModel):
    id: str
    threadId: str
    labelIds: Optional[List[str]] = None
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    internalDate: Optional[str] = None
    sizeEstimate: Optional[int] = None
    raw: Optional[str] = None
    payload: Optional[MessagePayload] = None

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    threadId: Optional[str] = None

class DraftEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    threadId: Optional[str] = None

class DraftEmailResponse(BaseModel):
    id: str
    message: EmailDetail

class AutoReplyRequest(BaseModel):
    prompt_template_id: str = "default_auto_reply"
    additional_instructions: Optional[str] = None

class GenerateSummaryRequest(BaseModel):
    prompt_template_id: str = "default_summary"
    additional_instructions: Optional[str] = None

class GenerateSummaryResponse(BaseModel):
    email_id: str
    summary: str
