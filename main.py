import os
import csv
import json
import asyncio
from dotenv import load_dotenv
from classifier import classify_company
from email_generator import gen_email
from utils.safeparse import safe_parse_json
from openai import AsyncOpenAI
from utils.exclusions import check_exclusion
from utils.csv_write import write_email_output_csv

def main():
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    csv_path = os.path.join(os.path.dirname(__file__), "in", "speakers.csv")
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 5:
                    break
                name = (row.get("Speaker Name") or "").strip()
                title = (row.get("Speaker Title") or "").strip()
                company = (row.get("Speaker Company") or "").strip()

                result = classify_company(company, title)
                parsed = safe_parse_json(result)

                out_path = os.path.join(os.path.dirname(__file__), "out", "email_output.csv")

                if not check_exclusion(parsed):
                    try:
                        email = asyncio.run(gen_email(name, title, parsed))
                        record = {
                            "Speaker Name": name,
                            "Speaker Title": title,
                            "Speaker Company": company,
                            "Company Category": parsed.get("category"),
                            "Email Subject": email.get("subject", ""),
                            "Email Body": email.get("body", ""),
                        }
                        write_email_output_csv(out_path, record)

                    except Exception as e:
                        print(f"Email generation error: {e}")
                else:
                    record = {
                        "Speaker Name": name,
                        "Speaker Title": title,
                        "Speaker Company": company,
                        "Company Category": parsed.get("category"),
                        "Email Subject": "",
                        "Email Body": "",
                    }
                    write_email_output_csv(out_path, record)
       
    except FileNotFoundError:
        print(f"Could not find CSV at {csv_path}")

if __name__ == "__main__":
    main()
