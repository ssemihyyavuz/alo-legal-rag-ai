from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import os
import urllib.robotparser
import time

url = "https://www.uscis.gov/administrative-appeals/aao-decisions/aao-non-precedent-decisions?uri_1=19&m=2&y=1&items_per_page=25"
headers = {"User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0)"}

# 🤖 robots.txt kontrolü
rp = urllib.robotparser.RobotFileParser()
rp.set_url("https://www.uscis.gov/robots.txt")
rp.read()

if not rp.can_fetch(headers["User-Agent"], url):
    print("🚫 robots.txt engelliyor, çıkılıyor.")
    exit()

# ✅ Sayfa çekimi
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

rows = soup.find_all("div", class_=re.compile("views-row"))
pdf_links = []

print(f"🔎 Toplam {len(rows)} adet belge bulundu.\n")

for i, row in enumerate(rows, 1):
    print(f"--- Row {i} ---")

    try:
        # 🔗 PDF Linkini bulmaya çalış
        link_divs = row.find_all("div", class_=re.compile("views-field.*title"))
        a_tag = None
        for div in link_divs:
            inner = div.find("div", class_="field-content")
            if inner:
                a = inner.find("a", href=True)
                if a and a["href"].endswith(".pdf"):
                    a_tag = a
                    break

        # 📅 Tarih bilgisi
        date_div = row.find("div", class_=re.compile("views-field.*field-display-date"))
        date_text = date_div.find("div", class_="field-content").text.strip() if date_div else None

        # 📂 Kategori bilgisi
        category_divs = row.find_all("div", class_="views-field")
        last_div = category_divs[-1] if category_divs else None
        category_text = last_div.find("div", class_="field-content").text.strip() if last_div else None

        if not all([a_tag, date_text, category_text]):
            print("❌ Gerekli alanlar eksik:")
            print(f"  a_tag: {a_tag}")
            print(f"  date_text: {date_text}")
            print(f"  category_text: {category_text}\n")
            continue

        if not re.search(r"February\s+\d{1,2},\s+2025", date_text):
            print("📆 Şubat 2025 değil, atlanıyor.\n")
            continue

        combined_text = f"{category_text} {a_tag.get_text(strip=True)}".lower()
        if "i-140" not in combined_text or "extraordinary ability" not in combined_text:
            print("🔍 Kriter eşleşmedi.")
            print(f"  Başlık: {a_tag.get_text(strip=True)}")
            print(f"  Kategori: {category_text}\n")
            continue

        full_url = "https://www.uscis.gov" + a_tag["href"]
        title_text = a_tag.get_text(strip=True)

        pdf_links.append({
            "url": full_url,
            "date": date_text,
            "category": category_text,
            "title": title_text
        })

        print(f"✅ Eklendi: {date_text} | {category_text} | {title_text}\n")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}\n")
        continue

# 📁 PDF klasörünü oluştur ve indir
save_dir = "pdfs"
os.makedirs(save_dir, exist_ok=True)

print(f"📦 {len(pdf_links)} adet PDF indirilecek:\n")

for idx, p in enumerate(pdf_links):
    pdf_url = p["url"]
    date = datetime.strptime(p["date"], "%B %d, %Y").strftime("%Y-%m-%d")
    filename = f"{date}_I140_EA_{idx+1}.pdf"
    filepath = os.path.join(save_dir, filename)

    print(f"📥 Downloading: {filename}")
    try:
        response = requests.get(pdf_url, headers=headers)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print("✅ Saved:", filepath)
        time.sleep(10)
    except Exception as e:
        print("❌ Error downloading:", pdf_url, "-", e)

print("\n🎉 Tamamlandı.")
