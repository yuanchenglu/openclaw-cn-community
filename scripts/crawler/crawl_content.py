import json
import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import time

OUTPUT_DIR = "clawd_docs"
PLAN_FILE = os.path.join(OUTPUT_DIR, "crawl_plan.json")
TOC_FILE = os.path.join(OUTPUT_DIR, "TOC.md")

def load_plan():
    with open(PLAN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_plan(plan):
    with open(PLAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

def update_toc(title, path):
    # Mark the item as completed in TOC.md
    # We look for the line containing the path and modify it.
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if path in line and "✓" not in line:
            # Insert checkmark
            line = line.replace("- [", "- [✓ ")
        new_lines.append(line)
        
    with open(TOC_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def fetch_and_convert(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # VitePress content is usually in .vp-doc or main
        content = soup.select_one('.vp-doc')
        if not content:
            content = soup.find('main')
            
        if not content:
            print(f"Could not find content for {url}")
            return None
            
        # Remove anchor links from headers to avoid clutter
        for anchor in content.select('.header-anchor'):
            anchor.decompose()
            
        # Convert to Markdown
        markdown = md(str(content), heading_style="ATX")
        return markdown
        
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main():
    plan = load_plan()
    
    total = len(plan)
    completed = sum(1 for item in plan if item['status'] == 'completed')
    
    print(f"Plan loaded. {completed}/{total} completed.")
    
    for item in plan:
        if item['status'] == 'pending':
            print(f"Processing: {item['title']} ({item['url']})")
            
            markdown = fetch_and_convert(item['url'])
            
            if markdown:
                save_path = item['save_path']
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {item['title']}\n\n")
                    f.write(f"Source: {item['url']}\n\n")
                    f.write(markdown)
                
                item['status'] = 'completed'
                save_plan(plan)
                update_toc(item['title'], os.path.relpath(save_path, OUTPUT_DIR))
                
                print(f"Saved to {save_path}")
                
                # Be nice to the server
                time.sleep(0.5)
            else:
                print(f"Failed to fetch content for {item['title']}")
                item['status'] = 'failed'
                save_plan(plan)

if __name__ == "__main__":
    main()
