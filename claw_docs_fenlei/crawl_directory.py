import requests
import json
import re
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://clawd.org.cn"
START_URL = "https://clawd.org.cn/start/getting-started"
OUTPUT_DIR = "clawd_docs"
TOC_FILE = os.path.join(OUTPUT_DIR, "TOC.md")
PLAN_FILE = os.path.join(OUTPUT_DIR, "crawl_plan.json")

def fetch_page(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8' # Force UTF-8
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_sidebar_data(html):
    # Look for the script that contains the site data
    # It usually looks like window.__VP_SITE_DATA__ = { ... } or similar in VitePress
    # Based on the curl output, it seems to be inside a script tag, likely valid JSON or JS object.
    
    # Let's try to find the specific pattern seen in the curl output
    # The curl output showed: ...sidebar":[{"text":"...
    # It might be part of a larger JSON object.
    
    # Regex to find the JSON-like structure. 
    # Since extracting full JS object with regex is hard, let's look for the specific script tag content.
    # It often starts with window.__VP_SITE_DATA__ = 
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Method 1: Look for the script tag with window.__VP_SITE_DATA__
    for script in soup.find_all('script'):
        if script.string and 'window.__VP_SITE_DATA__' in script.string:
            # Extract the JSON object
            content = script.string
            start_marker = 'window.__VP_SITE_DATA__ = '
            start_index = content.find(start_marker)
            if start_index != -1:
                json_str = content[start_index + len(start_marker):]
                # Remove trailing semicolon if present
                json_str = json_str.strip()
                if json_str.endswith(';'):
                    json_str = json_str[:-1]
                
                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from script: {e}")
                    # Try to regex it out if simple strip failed
                    match = re.search(r'({.+})', json_str, re.DOTALL)
                    if match:
                        try:
                            return json.loads(match.group(1))
                        except:
                            pass

    # Method 2: Parse from DOM (Sidebar) if JSON extraction fails
    print("JSON extraction failed, trying DOM parsing...")
    return parse_sidebar_from_dom(soup)

def parse_sidebar_from_dom(soup):
    # VitePress sidebar structure usually:
    # <div class="VPSidebar"> ... <div class="group"> ... </div> </div>
    # We need to reconstruct the structure.
    
    sidebar_items = []
    
    # Try to find the sidebar container
    sidebar = soup.find(class_="VPSidebar")
    if not sidebar:
        # Maybe it's not called VPSidebar or not rendered
        return None
        
    # This is complex because we need to handle nesting. 
    # Let's return a special structure or just a flat list if nesting is too hard.
    # But the user wants hierarchy.
    
    # Let's try to find groups
    groups = sidebar.find_all(class_="VPSidebarGroup")
    for group in groups:
        # Extract title
        title_el = group.find(class_="title-text")
        title = title_el.get_text(strip=True) if title_el else "Group"
        
        items = []
        # Find links
        links = group.find_all('a', class_="VPLink")
        for link in links:
            text_el = link.find(class_="text") or link
            text = text_el.get_text(strip=True)
            href = link.get('href')
            items.append({"text": text, "link": href})
            
        sidebar_items.append({"text": title, "items": items})
        
    if not sidebar_items:
        # Fallback to finding all sidebar links
        links = sidebar.find_all('a')
        for link in links:
             sidebar_items.append({"text": link.get_text(strip=True), "link": link.get('href')})
             
    return {"themeConfig": {"sidebar": sidebar_items}}


def process_sidebar(sidebar_data):
    # Sidebar can be a list or a dict (for multi-sidebar). 
    # Based on curl output, it looks like a list: "sidebar":[{"text":...}]
    
    # If it's a dict (path -> sidebar), we need to find the one matching our path or merge them.
    # But usually for simple sites it's a list.
    
    # The extracted data from VP_SITE_DATA usually has a 'themeConfig' key which contains 'sidebar'.
    
    if 'themeConfig' in sidebar_data:
        sidebar = sidebar_data['themeConfig'].get('sidebar')
    else:
        sidebar = sidebar_data.get('sidebar')
        
    if not sidebar:
        print("No sidebar found in data.")
        return []

    # If sidebar is a dict (different sidebars for different paths), we might want to capture all of them or just the default.
    # For now, let's assume it's a list or we take the values if it's a dict.
    
    items = []
    
    if isinstance(sidebar, dict):
        # Merge all lists from the dict
        for key, val in sidebar.items():
            if isinstance(val, list):
                items.extend(val)
    elif isinstance(sidebar, list):
        items = sidebar
        
    return items

def build_toc_and_plan(items, level=0):
    toc_lines = []
    plan_items = []
    
    for item in items:
        text = item.get('text', 'Untitled')
        link = item.get('link')
        sub_items = item.get('items', [])
        
        indent = "  " * level
        
        if link:
            # Normalize link
            full_url = urljoin(BASE_URL, link)
            
            # Skip external links that don't start with base url
            if not full_url.startswith(BASE_URL):
                toc_lines.append(f"{indent}- [{text}]({full_url})")
                # We don't crawl external links
                continue
            
            # Create a safe filename
            rel_path = link.strip('/')
            if not rel_path:
                rel_path = "index"
            
            # Remove .html if present
            if rel_path.endswith('.html'):
                rel_path = rel_path[:-5]
            
            # Append .md
            rel_path += ".md"
                
            # Handle hash links
            if '#' in rel_path:
                rel_path = rel_path.split('#')[0]
            
            save_path = os.path.join(OUTPUT_DIR, rel_path)
            
            toc_lines.append(f"{indent}- [{text}]({rel_path})")
            
            plan_items.append({
                "title": text,
                "url": full_url,
                "save_path": save_path,
                "status": "pending"
            })
        else:
            toc_lines.append(f"{indent}- {text}")
            
        if sub_items:
            sub_toc, sub_plan = build_toc_and_plan(sub_items, level + 1)
            toc_lines.extend(sub_toc)
            plan_items.extend(sub_plan)
            
    return toc_lines, plan_items

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    html = fetch_page(START_URL)
    if not html:
        return

    data = extract_sidebar_data(html)
    if not data:
        # Fallback: maybe the JSON is inside a slightly different structure or simply formatted differently
        # Let's try to find "sidebar": [...] pattern directly if the big object fails
        match = re.search(r'"sidebar"\s*:\s*(\[.+?\])(?:,\s*"|\})', html, re.DOTALL)
        if match:
            try:
                sidebar_list = json.loads(match.group(1))
                data = {"themeConfig": {"sidebar": sidebar_list}}
            except:
                print("Fallback regex failed to parse JSON.")
                return
        else:
            print("Could not extract sidebar data.")
            return

    sidebar_items = process_sidebar(data)
    toc_lines, plan_items = build_toc_and_plan(sidebar_items)
    
    # Write TOC
    with open(TOC_FILE, 'w', encoding='utf-8') as f:
        f.write("# Table of Contents\n\n")
        f.write("\n".join(toc_lines))
        
    # Write Plan
    with open(PLAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(plan_items, f, indent=2, ensure_ascii=False)
        
    print(f"Generated TOC with {len(toc_lines)} lines and Plan with {len(plan_items)} items.")

if __name__ == "__main__":
    main()
