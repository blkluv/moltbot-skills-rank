import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_moltbot_skills():
    print("Execution started: Fetching data from ClawdHub...")
    url = "https://clawdhub.com/skills"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ClawdHub uses different card styles. We search for generic containers
        # that likely contain a skill entry.
        cards = soup.find_all(['div', 'section'], class_=re.compile(r'card|group|relative'))
        
        extracted_skills = []
        seen_names = set() # Avoid duplicates

        for card in cards:
            title_el = card.find(['h3', 'h4', 'h2'])
            if not title_el:
                continue
                
            name = title_el.get_text(strip=True)
            if name in seen_names or len(name) < 2:
                continue
            
            # Look for description in nearby paragraph tags
            desc_el = card.find('p')
            description = desc_el.get_text(strip=True) if desc_el else "No description provided."
            
            # Look for GitHub link
            github_link = card.find('a', href=re.compile(r'github\.com'))
            repo_url = github_link['href'] if github_link else "#"
            
            # Star counting logic
            stars_count = 0
            star_text = card.get_text()
            # Look for numbers near a star emoji or the word "stars"
            stars_match = re.search(r'(\d+)\s*(?:stars|⭐)', star_text, re.IGNORECASE)
            if stars_match:
                stars_count = int(stars_match.group(1))
            else:
                # Fallback: just find any number in the card that isn't too long
                num_matches = re.findall(r'\b\d+\b', star_text)
                if num_matches:
                    stars_count = int(num_matches[0])

            extracted_skills.append({
                "name": name,
                "desc": description,
                "url": repo_url,
                "stars": stars_count
            })
            seen_names.add(name)
            
        # Structure data with the timestamp
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": extracted_skills
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Scraped {len(extracted_skills)} skills.")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    scrape_moltbot_skills()
