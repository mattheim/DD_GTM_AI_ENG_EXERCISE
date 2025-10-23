def check_exclusion(parsed):
    """Determine if outreach should be skipped based on classification.

    Rules:
    - If category is 'competitor' or 'partner' -> skip (return True).
    - Otherwise -> proceed (return False).

    Falls back to the 'exclusion' field if present for compatibility.
    """
    data = parsed or {}
    category = str(data.get("category", "")).strip().lower()
    exclusion = str(data.get("exclusion", "")).strip().lower()

    excluded = category in ("competitor", "partner") or exclusion in ("competitor", "partner")
    if excluded:
        reason = category if category in ("competitor", "partner") else (exclusion or "unspecified")
        print(f"{data.get("company")} > Excluded ({reason}) — skip outreach")
        return True
    print(f"{data.get("company")} > Not excluded — proceed with outreach")
    return False
