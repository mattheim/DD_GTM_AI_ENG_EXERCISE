import os
import json
from typing import Literal, TypedDict, Dict
from openai import OpenAI, AsyncOpenAI
from prompts import CLASSIFIER_PROMPT
from utils.safeparse import safe_parse_json

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
        ],
        # Ask the model to return strict JSON
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content.strip()

    # Parse and sanitize any code fences or malformed JSON
    data = safe_parse_json(content)

    # Normalize output keys and values
    result: CompanyClassification = {
        "company": (data.get("company") or company or "").strip(),
        "summary": (data.get("summary") or "").strip(),
        "category": (data.get("category") or "Other").strip(),
    }

    # Constrain category to allowed set
    allowed = {"Builder", "Owner", "Partner", "Competitor", "Other"}
    if result["category"] not in allowed:
        result["category"] = "Other"

    return result
