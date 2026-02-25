import urllib.request
import io
import json
import re
import os
import pypdf

url = "https://static.thatsup.website/152/78855/Svenska-menyn-vecka-9.pdf?v=1771615900"

def fetch_and_parse():
    print("Fetching PDF...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        pdf_file = io.BytesIO(response.read())

    reader = pypdf.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in reader.pages])

    # Clean whitespace
    normalized_text = re.sub(r'\n', ' ', text)
    normalized_text = re.sub(r'\s+', ' ', normalized_text)

    # Fast forward to "PLAT DU JOUR"
    plat_idx = normalized_text.find("PLAT DU JOUR")
    if plat_idx != -1:
        normalized_text = normalized_text[plat_idx:]

    days = [
        {"id": "MÅNDAG", "label": "Måndag"},
        {"id": "TISDAG", "label": "Tisdag"},
        {"id": "ONSDAG", "label": "Onsdag"},
        {"id": "TORSDAG", "label": "Torsdag"},
        {"id": "FREDAG", "label": "Fredag"},
        {"id": "VECKANS VEGETARISKA", "label": "Veckans Vegetariska"}
    ]

    menu_items = []
    
    for i, current_day in enumerate(days):
        day_id = current_day["id"]
        pos = normalized_text.find(day_id)
        if pos != -1:
            next_positions = []
            for j in range(i + 1, len(days)):
                next_pos = normalized_text.find(days[j]["id"], pos + len(day_id))
                if next_pos != -1:
                    next_positions.append(next_pos)
            
            sweet_wines_pos = normalized_text.find("SWEET WINES", pos + len(day_id))
            
            end_pos = min(next_positions) if next_positions else sweet_wines_pos
            if end_pos == -1 and sweet_wines_pos == -1:
                end_pos = pos + 250 # Fallback 
            
            raw_dish = normalized_text[pos + len(day_id):end_pos].strip()
            
            # Remove "seedling" artifact
            raw_dish = raw_dish.replace("seedling", "").strip()
            raw_dish = re.sub(r'\s{2,}', ' ', raw_dish)
            
            menu_items.append({
                "day": current_day["label"],
                "dish": raw_dish
            })

    # Save to JSON
    with open("menu.json", "w", encoding="utf-8") as f:
        json.dump(menu_items, f, ensure_ascii=False, indent=4)
        print("menu.json written successfully.")

if __name__ == "__main__":
    fetch_and_parse()
