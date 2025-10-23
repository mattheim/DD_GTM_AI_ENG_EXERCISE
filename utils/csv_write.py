# utils.py
import os
import csv

def write_email_output_csv(out_path: str, record: dict):
    """
    Appends a record to the email_output.csv file.
    Automatically creates the directory and writes headers if needed.
    """

    headers = [
        "Speaker Name",
        "Speaker Title",
        "Speaker Company",
        "Company Category",
        "Email Subject",
        "Email Body",
    ]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    file_exists = os.path.exists(out_path)

    with open(out_path, "a", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Speaker Name": record.get("Speaker Name", ""),
            "Speaker Title": record.get("Speaker Title", ""),
            "Speaker Company": record.get("Speaker Company", ""),
            "Company Category": record.get("Company Category", ""),
            "Email Subject": record.get("Email Subject", ""),
            "Email Body": record.get("Email Body", ""),
        })
