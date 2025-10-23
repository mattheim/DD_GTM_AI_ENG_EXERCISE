import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from utils.safeparse import safe_parse_json
from prompts import EMAIL_GEN_SYSTEM_PROMPT

async def gen_email(name: str, title: str, parsed: dict) -> dict:
    async with AsyncOpenAI() as client:
        email = await generate_email(
            client, speaker_name=name, speaker_title=title, data=parsed
        )
        return email

async def generate_email(
    client: AsyncOpenAI,
    *,
    speaker_name: str,
    speaker_title: str,
    data: Any
) -> Dict[str, str]:
    """Generate an email using arbitrary JSON input.

    The `data` argument can be any JSON-serializable object or a JSON string.
    No specific keys are required; the JSON is included as context.
    Returns a dict with keys: subject, body.
    """
    # Normalize input to something concise we can pass as context
    context_obj: Any
    if isinstance(data, str):
        parsed = safe_parse_json(data)
        context_obj = parsed
    else:
        context_obj = data

    try:
        context_json = json.dumps(context_obj, ensure_ascii=False)
    except Exception:
        context_json = str(context_obj)

    system_prompt = (
        "You are a helpful outreach assistant. "
        "Write short, friendly, value-focused emails for conference speakers. "
        "Always respond as strict JSON with keys 'subject' and 'body'."
        f"f{EMAIL_GEN_SYSTEM_PROMPT}"
        
    )
    user_prompt = (
        f"Speaker: {speaker_name or 'there'} ({speaker_title or ''})\n"
        f"Context JSON: {context_json}\n\n"
        "Write a 2–3 sentence invite to visit DroneDeploy's booth #42. "
        "Focus on relevance to the speaker based on the context. Include a clear CTA."
    )

    resp = await client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    content = (resp.choices[0].message.content or "").strip()
    try:
        data = json.loads(content)
    except Exception:
        # If the model didn't return JSON, use the content as the body
        data = {"subject": "Visit DroneDeploy at Booth #42", "body": content}

    return {
        "subject": (data.get("subject") or "Visit DroneDeploy at Booth #42").strip(),
        "body": (data.get("body") or "").strip(),
    }
