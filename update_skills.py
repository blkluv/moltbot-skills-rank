import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_moltbot_skills():
    print("Scraper started...")
    url = "https://clawdhub.com/skills"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        extracted_skills = []
        
        # We search for all links that point to GitHub - these are our skills!
        github_links = soup.find_all('a', href=re.compile(r'github\.com/'))
        
        for link in github_links:
            # The parent container usually holds the name and description
            container = link.find_parent(['div', 'section'])
            if not container: continue
            
            # Find the name (usually in a heading)
            name_el = container.find(['h2', 'h3', 'h4'])
            name = name_el.get_text(strip=True) if name_el else "Unknown Tool"
            
            # Find the description (usually in a paragraph)
            desc_el = container.find('p')
            description = desc_el.get_text(strip=True) if desc_el else "Fast tool for Moltbot."
            
            # Find stars (look for numbers near a star emoji)
            stars_match = re.search(r'(\d+)', container.get_text())
            stars = int(stars_match.group(1)) if stars_match else 0
            
            extracted_skills.append({
                "name": name,
                "desc": description,
                "url": link['href'],
                "stars": stars
            })
            
        # If the first method fails, try finding cards by class
        if not extracted_skills:
            cards = soup.select('.bg-card, .group, .relative')
            for card in cards:
                # (similar logic here as backup)
                pass

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": extracted_skills
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Found {len(extracted_skills)} skills.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_moltbot_skills()
