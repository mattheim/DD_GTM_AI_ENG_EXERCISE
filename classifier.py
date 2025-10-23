import os
import json
from typing import Literal, TypedDict, Dict
from openai import OpenAI, AsyncOpenAI
from prompts import CLASSIFIER_PROMPT

class CompanyClassification(TypedDict):
    company: str
    summary: str
    category: str

def classify_company(company: str, title: str | None = None) -> CompanyClassification:
    """
    summarize and classify a company into Builder, Owner, Partner, or Competitor
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt =f"{CLASSIFIER_PROMPT}"
    user_prompt = f"\nCompany: {company}\nTitle: {title or ''}\n\nRespond only in valid JSON."

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    content = response.choices[0].message.content.strip()

    # Parse the model’s JSON output safely
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "company": company,
            "summary": content,
            "category": content
        }

    return data