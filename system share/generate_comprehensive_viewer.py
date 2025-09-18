#!/usr/bin/env python3
"""
Generate comprehensive static encyclopedia viewer with all content from system share
"""

import os
import json
import re
from pathlib import Path

def escape_js_string(text):
    """Escape string for JavaScript embedding"""
    if not text:
        return ""
    # Escape backslashes, quotes, and newlines
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n')
    text = text.replace('\r', '')
    return text

def read_markdown_file(file_path):
    """Read markdown file and return content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def categorize_file(file_path):
    """Categorize file based on path and content"""
    path_str = str(file_path).lower()
    
    if 'foundations' in path_str:
        if any(x in path_str for x in ['magic', 'spell', 'polymorph']):
            return 'magic'
        elif any(x in path_str for x in ['nss', 'capital', 'employment', 'market', 'economic']):
            return 'economics'
        elif any(x in path_str for x in ['will', 'daemon', 'philosophy', 'manifestation']):
            return 'philosophy'
        elif any(x in path_str for x in ['technical', 'architecture', 'computational', 'discovery', 'ar_phase']):
            return 'technical'
        else:
            return 'foundation'
    elif 'historical' in path_str:
        return 'historical'
    elif 'dialectic' in path_str:
        return 'dialectic'
    elif 'polymorphic' in path_str:
        return 'polymorphic'
    else:
        return 'other'

def extract_title(content):
    """Extract title from markdown content"""
    if not content:
        return "Untitled"
    
    # Look for first h1 heading
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    
    # Fallback to filename
    return "Untitled"

def extract_description(content, max_length=200):
    """Extract description from markdown content"""
    if not content:
        return "No description available"
    
    # Remove markdown formatting
    text = re.sub(r'#+\s*', '', content)  # Remove headers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
    text = re.sub(r'`(.*?)`', r'\1', text)  # Remove code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links
    
    # Get first paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if paragraphs:
        desc = paragraphs[0]
        if len(desc) > max_length:
            desc = desc[:max_length] + "..."
        return desc
    
    return "No description available"

def scan_directory(directory):
    """Scan directory for markdown files and extract content"""
    entries = {}
    directory = Path(directory)
    
    # Scan all markdown files recursively
    for md_file in directory.rglob('*.md'):
        if md_file.name.startswith('.'):
            continue
            
        content = read_markdown_file(md_file)
        if not content:
            continue
            
        # Create entry key from file path
        rel_path = md_file.relative_to(directory)
        key = str(rel_path).replace('/', '_').replace('\\', '_').replace('.md', '')
        
        # Categorize file
        file_type = categorize_file(md_file)
        
        # Extract metadata
        title = extract_title(content)
        description = extract_description(content)
        
        # Extract keywords from content (simple approach)
        keywords = []
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'there', 'when', 'your', 'can', 'said', 'she', 'use', 'her', 'many', 'some', 'these', 'would', 'other', 'into', 'has', 'more', 'very', 'what', 'know', 'just', 'first', 'also', 'after', 'back', 'well', 'work', 'life', 'only', 'still', 'new', 'want', 'because', 'any', 'may', 'say', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, freq in keywords]
        
        entries[key] = {
            'title': title,
            'type': file_type,
            'category': file_type.title(),
            'description': description,
            'keywords': keywords,
            'content': content,
            'path': str(rel_path)
        }
    
    return entries

def generate_js_entries(entries):
    """Generate JavaScript entries object"""
    js_lines = ['const encyclopediaEntries = {']
    
    for key, entry in entries.items():
        js_lines.append(f'    "{key}": {{')
        js_lines.append(f'        title: "{escape_js_string(entry["title"])}",')
        js_lines.append(f'        type: "{entry["type"]}",')
        js_lines.append(f'        category: "{entry["category"]}",')
        js_lines.append(f'        description: "{escape_js_string(entry["description"])}",')
        js_lines.append(f'        keywords: {json.dumps(entry["keywords"])},')
        js_lines.append(f'        content: `{entry["content"]}`.replace(/\\`/g, "`"),')
        js_lines.append(f'        path: "{entry["path"]}"')
        js_lines.append('    },')
    
    js_lines.append('};')
    return '\n'.join(js_lines)

def main():
    """Main function to generate comprehensive viewer"""
    system_share_dir = Path('.')
    
    print("Scanning current directory for markdown files...")
    entries = scan_directory(system_share_dir)
    
    print(f"Found {len(entries)} markdown files")
    
    # Generate JavaScript entries
    js_entries = generate_js_entries(entries)
    
    # Read the base HTML template
    with open('encyclopedia-static-viewer.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace the entries section
    start_marker = '// Comprehensive Encyclopedia entries data with embedded content'
    end_marker = '};'
    
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        new_content = html_content[:start_idx] + js_entries + html_content[end_idx:]
        
        # Write the comprehensive viewer
        with open('encyclopedia-comprehensive-viewer.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Generated comprehensive viewer: encyclopedia-comprehensive-viewer.html")
        print(f"Included {len(entries)} entries from all subdirectories")
    else:
        print("Error: Could not find entries section in template")

if __name__ == "__main__":
    main()
