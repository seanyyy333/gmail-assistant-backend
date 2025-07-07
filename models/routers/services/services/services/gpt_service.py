from typing import Optional
from openai import OpenAI
from ..models.prompt import DEFAULT_AUTO_REPLY_TEMPLATE, DEFAULT_SUMMARY_TEMPLATE

# Initialize the OpenAI client
client = OpenAI()

def generate_auto_reply(email_content: str, additional_instructions: Optional[str] = "") -> str:
    prompt = DEFAULT_AUTO_REPLY_TEMPLATE.format(
        additional_instructions=additional_instructions or "",
        email_content=email_content
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful email assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def generate_summary(email_content: str, additional_instructions: Optional[str] = "") -> str:
    prompt = DEFAULT_SUMMARY_TEMPLATE.format(
        additional_instructions=additional_instructions or "",
        email_content=email_content
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful email summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()
