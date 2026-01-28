import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_moltbot_skills():
    print("Scraper started: Advanced Mode...")
    url = "https://clawdhub.com/skills"
    
    # We use a very common browser signature to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        # If the site uses Cloudflare or heavy JS, the status might be 200 but the body is empty
        soup = BeautifulSoup(response.text, 'html.parser')
        
        extracted_skills = []
        
        # METHOD 1: Look for any "Card" like structures (Tailwind classes are common)
        # We look for containers that have a link to GitHub
        potential_cards = soup.find_all(['div', 'article', 'section'])
        
        for card in potential_cards:
            link = card.find('a', href=re.compile(r'github\.com/'))
            if not link:
                continue
                
            # If we found a GitHub link, this is likely a skill card!
            name = "Unknown Skill"
            # Look for headings inside this card
            for tag in ['h1', 'h2', 'h3', 'h4', 'strong', 'b']:
                found_name = card.find(tag)
                if found_name:
                    name = found_name.get_text(strip=True)
                    break
            
            # Look for description (paragraphs)
            desc = "No description found."
            found_desc = card.find('p')
            if found_desc:
                desc = found_desc.get_text(strip=True)
            
            # Look for stars (often a number next to a SVG or ⭐)
            stars = 0
            text_content = card.get_text()
            star_match = re.search(r'(\d+)\s*stars?', text_content, re.IGNORECASE)
            if star_match:
                stars = int(star_match.group(1))

            extracted_skills.append({
                "name": name,
                "desc": desc,
                "url": link['href'],
                "stars": stars
            })

        # REMOVE DUPLICATES (Cards often nest inside each other)
        unique_skills = {s['url']: s for s in extracted_skills}.values()
        final_list = list(unique_skills)

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Found {len(final_list)} unique skills.")

    except Exception as e:
        print(f"Scraper Failed: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_moltbot_skills()
