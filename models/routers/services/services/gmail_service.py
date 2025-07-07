import os
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
from typing import List, Optional

from ..models.email import EmailDetail, MessagePayload, MessagePartHeader, MessagePartBody, MessagePart

def parse_email_payload(payload: dict) -> Optional[MessagePayload]:
    if payload is None:
        return None

    parts = [parse_email_payload(p) for p in payload.get('parts', [])] if payload.get('parts') else None
    body_data = payload.get('body', {})
    parsed_body = MessagePartBody(**body_data) if body_data else None

    return MessagePayload(
        partId=payload.get('partId'),
        mimeType=payload.get('mimeType'),
        filename=payload.get('filename'),
        headers=[MessagePartHeader(**h) for h in payload.get('headers', [])] if payload.get('headers') else None,
        body=parsed_body,
        parts=parts
    )

def get_part_data(part_body: MessagePartBody) -> Optional[bytes]:
    if part_body and part_body.data:
        data = part_body.data.replace('-', '+').replace('_', '/')
        padding = len(data) % 4
        if padding > 0:
            data += '=' * (4 - padding)
        try:
            return base64.b64decode(data)
        except Exception as e:
            print(f"Error decoding part data: {e}")
            return None
    return None

def get_email_body(payload: Optional[MessagePayload]) -> Optional[str]:
    if not payload:
        return None

    def find_body_part(parts: List[MessagePart]) -> Optional[MessagePart]:
        for part in parts:
            if part.mimeType == 'text/plain':
                return part
        for part in parts:
            if part.mimeType == 'text/html':
                return part
            if part.parts:
                nested_part = find_body_part(part.parts)
                if nested_part:
                    return nested_part
        return None

    body_part = None
    if payload.mimeType in ['text/plain', 'text/html']:
        body_part = MessagePart(
            partId=payload.partId,
            mimeType=payload.mimeType,
            filename=payload.filename,
            headers=payload.headers,
            body=payload.body,
            parts=None
        )
    elif payload.parts:
        body_part = find_body_part(payload.parts)

    if body_part and body_part.body:
        data = get_part_data(body_part.body)
        if data:
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return data.decode('latin-1')
                except Exception:
                    return data.decode('utf-8', errors='ignore')

    return None

def fetch_emails(service, user_id='me', label_ids=['INBOX'], max_results=10) -> List[EmailDetail]:
    try:
        results = service.users().messages().list(
            userId=user_id, labelIds=label_ids, maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            print("No messages found.")
            return []

        email_list = []
        for message in messages:
            try:
                msg = service.users().messages().get(
                    userId=user_id, id=message['id'], format='full'
                ).execute()

                parsed_email = EmailDetail(
                    id=msg.get('id', 'N/A'),
                    threadId=msg.get('threadId', 'N/A'),
                    labelIds=msg.get('labelIds'),
                    snippet=msg.get('snippet'),
                    historyId=msg.get('historyId'),
                    internalDate=msg.get('internalDate'),
                    sizeEstimate=msg.get('sizeEstimate'),
                    raw=msg.get('raw'),
                    payload=parse_email_payload(msg.get('payload'))
                )
                email_list.append(parsed_email)

            except HttpError as e:
                print(f"API error fetching message {message['id']}: {e}")
                email_list.append(EmailDetail(id=message.get('id', 'ErrorID'), threadId=message.get('threadId', 'ErrorThread'), snippet=f"API error: {e}"))

            except Exception as e:
                print(f"Unexpected error fetching message {message['id']}: {e}")
                email_list.append(EmailDetail(id=message.get('id', 'ErrorID'), threadId=message.get('threadId', 'ErrorThread'), snippet=f"Unexpected error: {e}"))

        return email_list

    except HttpError as e:
        print(f"API error listing emails: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error listing emails: {e}")
        return []

def fetch_email_content(service, email_id: str, user_id='me', format='full') -> Optional[EmailDetail]:
    try:
        msg = service.users().messages().get(userId=user_id, id=email_id, format=format).execute()
        return EmailDetail(
            id=msg.get('id', 'N/A'),
            threadId=msg.get('threadId', 'N/A'),
            labelIds=msg.get('labelIds'),
            snippet=msg.get('snippet'),
            historyId=msg.get('historyId'),
            internalDate=msg.get('internalDate'),
            sizeEstimate=msg.get('sizeEstimate'),
            raw=msg.get('raw'),
            payload=parse_email_payload(msg.get('payload'))
        )
    except HttpError as e:
        print(f"API error fetching email {email_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching email {email_id}: {e}")
        return None

def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': encoded_message}

def send_email(service, to: str, subject: str, body: str, threadId: Optional[str] = None, user_id='me'):
    try:
        message_body = create_message(user_id, to, subject, body)
        if threadId:
            message_body['threadId'] = threadId
        sent_message = service.users().messages().send(userId=user_id, body=message_body).execute()
        print(f"Message sent: {sent_message.get('id')}")
        return sent_message
    except HttpError as e:
        print(f"API error sending email: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error sending email: {e}")
        return None
