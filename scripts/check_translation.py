import os
import re

DOCS_DIR = "clawd_docs"

def is_chinese_char(cp):
    return 0x4E00 <= cp <= 0x9FFF

def calculate_chinese_density(text):
    # Remove code blocks ```...```
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code `...`
    text = re.sub(r'`[^`]*`', '', text)
    # Remove links [text](url) - keep text, remove url? 
    # Actually, links often contain English urls, let's keep the text part but maybe it's fine.
    # Let's just remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    total_chars = 0
    chinese_chars = 0
    
    for char in text:
        if char.isspace():
            continue
        total_chars += 1
        if is_chinese_char(ord(char)):
            chinese_chars += 1
            
    if total_chars == 0:
        return 0
        
    return chinese_chars / total_chars

def main():
    print(f"{'File':<60} | {'Density':<8} | {'Status'}")
    print("-" * 80)
    
    low_density_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                density = calculate_chinese_density(content)
                
                # Threshold: if less than 20% Chinese, it's likely English or very sparse
                status = "OK"
                if density < 0.2:
                    status = "LOW"
                    low_density_files.append((file_path, density))
                elif density < 0.5:
                    status = "MIXED"
                    
                print(f"{os.path.relpath(file_path, DOCS_DIR):<60} | {density:.2%}   | {status}")
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    print("\nFiles needing attention:")
    for f, d in low_density_files:
        print(f"{f} ({d:.2%})")

if __name__ == "__main__":
    main()
