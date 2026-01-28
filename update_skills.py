import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Persistent Harvester (Anti-Virtual-Scroll Mode)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # We use a large viewport to see more items at once
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        page.wait_for_timeout(5000)

        all_skills_dict = {}
        
        # We will perform many small scrolls to catch items before they are unmounted
        # On infinite scroll sites, small increments are more reliable
        for i in range(50): 
            # 1. Capture everything currently in the 'Window'
            # We use evaluate to get the raw data directly from the DOM
            current_view_items = page.evaluate("""() => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="github.com/"]'));
                
                links.forEach(link => {
                    // Navigate up to find the card container
                    const card = link.closest('div');
                    if (card) {
                        const title = card.querySelector('h1, h2, h3, h4, h5, strong')?.innerText || "Unknown";
                        const desc = card.querySelector('p')?.innerText || "";
                        results.append({ url: link.href, name: title.trim(), desc: desc.trim() });
                    }
                });
                return results;
            }""")

            # 2. Add to our persistent dictionary (GitHub URL is the unique ID)
            for item in current_view_items:
                if item['url'] not in all_skills_dict and len(item['name']) > 2:
                    all_skills_dict[item['url']] = {
                        "name": item['name'],
                        "desc": item['desc'],
                        "url": item['url'],
                        "stars": 0
                    }

            # 3. Small scroll to trigger the next 'batch' of the virtual list
            page.mouse.wheel(0, 400) 
            page.wait_for_timeout(800) # Quick pause for data fetch
            
            if i % 10 == 0:
                print(f"Progress: Captured {len(all_skills_dict)} total skills so far...")

        final_list = list(all_skills_dict.values())
        
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"FINISHED! Saved {len(final_list)} unique skills to skills.json.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()
