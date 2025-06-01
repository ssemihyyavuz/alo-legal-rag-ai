import os
import re

text_dir = "texts"

for filename in os.listdir(text_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(text_dir, filename), "r", encoding="utf-8") as f:
            text = f.read()

        # 🔹 Tarihi çek
        date_match = re.search(r"(?i)^\s*date:\s*([A-Z]{3,}\.? \d{1,2}, \d{4})", text, re.MULTILINE)
        date = date_match.group(1) if date_match else "Unknown"

        # 🔹 ORDER kararını al
        order_text = ""
        order_match = re.search(r"ORDER:\s+(.+?)(\n|\Z)", text, re.DOTALL | re.IGNORECASE)
        if order_match:
            order_text = order_match.group(1).strip()

        # 🔹 ORDER içinde geçen belirli karar türleri
        if "appeal is dismissed" in order_text.lower():
            outcome = "Dismissed"
        elif "appeal is sustained" in order_text.lower():
            outcome = "Sustained"
        elif "motion to reopen is dismissed" in order_text.lower():
            outcome = "Motion to Reopen Dismissed"
        elif "motion to reconsider is dismissed" in order_text.lower():
            outcome = "Motion to Reconsider Dismissed"
        elif "decision is withdrawn" in order_text.lower() and "remanded" in order_text.lower():
            outcome = "Remanded"
        else:
            outcome = "Unknown"

        # 🔹 Başlık tahmini (ilk 10 satırda "Appeal of", "Motion on" geçen satır varsa)
        lines = text.splitlines()
        title = "Unknown"
        for line in lines[:10]:
            if "Appeal of" in line or "Motion on" in line:
                title = line.strip()
                break

        print(f"📄 {filename}")
        print(f"🗓️ Date: {date}")
        print(f"📌 Outcome: {outcome}")
        print(f"📑 Title: {title}")
        print("-----\n") 