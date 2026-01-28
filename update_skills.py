import json
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching headless browser...")
    with sync_playwright() as p:
        # 1. Start browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 2. Go to site and WAIT for content to load
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        
        # 3. Give it 5 extra seconds just in case
        page.wait_for_timeout(5000)
        
        extracted_skills = []
        
        # 4. Find all GitHub links as the 'anchor' for each skill
        # This version is robust even if the design changes
        links = page.query_selector_all("a[href*='github.com']")
        print(f"Detected {len(links)} potential links. Filtering...")

        for link in links:
            href = link.get_attribute("href")
            # Get the parent container box
            # Usually skills are inside a 'div' that has a 'card' or 'group' class
            container = link.evaluate_handle("el => el.closest('div, section')").as_element()
            
            if container:
                # Get the name from the largest heading
                name_el = container.query_selector("h1, h2, h3, h4")
                name = name_el.inner_text().strip() if name_el else "Unknown Skill"
                
                # Get description from paragraph
                desc_el = container.query_selector("p")
                desc = desc_el.inner_text().strip() if desc_el else "Moltbot capability."
                
                # Look for stars (numbers near a star icon)
                stars = 0
                full_text = container.inner_text()
                import re
                star_match = re.search(r'(\d+)\s*stars?', full_text, re.I)
                if star_match:
                    stars = int(star_match.group(1))

                extracted_skills.append({
                    "name": name,
                    "desc": desc,
                    "url": href,
                    "stars": stars
                })

        # Remove duplicates
        unique_skills = {s['url']: s for s in extracted_skills}.values()
        final_list = list(unique_skills)

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Saved {len(final_list)} unique skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()
