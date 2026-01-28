import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Deep Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to ClawdHub Skills...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        
        # --- NEW: Scroll down to load all dynamic content ---
        print("Scrolling to load all skills...")
        for _ in range(5): # Scroll 5 times to trigger lazy-loading
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1000)
            
        # Final wait for any last elements to appear
        page.wait_for_timeout(3000)
        
        extracted_skills = []
        
        # --- NEW: Improved selection logic ---
        # We look for all containers that likely represent a skill card
        # On ClawdHub, these are usually divs with 'group' or specific card classes
        cards = page.query_selector_all("div.group, div.relative.border, div.bg-card")
        print(f"Analyzing {len(cards)} potential skill cards...")

        for card in cards:
            # Look for the GitHub link inside this specific card
            link_el = card.query_selector("a[href*='github.com']")
            if not link_el:
                continue
                
            href = link_el.get_attribute("href")
            
            # Extract name from the heading
            name_el = card.query_selector("h1, h2, h3, h4, font")
            name = name_el.inner_text().strip() if name_el else "Unknown Skill"
            
            # Extract description from the paragraph
            desc_el = card.query_selector("p")
            desc = desc_el.inner_text().strip() if desc_el else "Advanced Moltbot tool."
            
            # Extract stars using regex from the card text
            full_text = card.inner_text()
            stars = 0
            star_match = re.search(r'(\d+)\s*stars?', full_text, re.I)
            if star_match:
                stars = int(star_match.group(1))

            extracted_skills.append({
                "name": name,
                "desc": desc,
                "url": href,
                "stars": stars
            })

        # Remove duplicates based on the GitHub URL
        unique_skills = {s['url']: s for s in extracted_skills}.values()
        final_list = list(unique_skills)

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Saved {len(final_list)} unique skills to skills.json.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()
