#!/usr/bin/env python3
"""
Generate complete deployable website from system share documents
"""

import os
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return ""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text

def escape_js_string(text):
    """Escape string for JavaScript embedding"""
    if not text:
        return ""
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

def extract_keywords(content):
    """Extract keywords from content"""
    if not content:
        return []
    
    # Extract meaningful words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
    word_freq = {}
    
    # Common words to exclude
    stop_words = {
        'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 
        'which', 'their', 'time', 'will', 'about', 'there', 'when', 'your', 'can', 
        'said', 'she', 'use', 'her', 'many', 'some', 'these', 'would', 'other', 'into', 
        'has', 'more', 'very', 'what', 'know', 'just', 'first', 'also', 'after', 'back', 
        'well', 'work', 'life', 'only', 'still', 'new', 'want', 'because', 'any', 'may', 
        'say', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made'
    }
    
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
    return [word for word, freq in keywords]

def scan_documents(system_share_dir):
    """Scan all documents in system share directory"""
    entries = {}
    system_share_path = Path(system_share_dir)
    
    # Scan all markdown files recursively
    for md_file in system_share_path.rglob('*.md'):
        if md_file.name.startswith('.'):
            continue
            
        content = read_markdown_file(md_file)
        if not content:
            continue
            
        # Create entry key from file path
        rel_path = md_file.relative_to(system_share_path)
        key = str(rel_path).replace('/', '_').replace('\\', '_').replace('.md', '')
        
        # Categorize file
        file_type = categorize_file(md_file)
        
        # Extract metadata
        title = extract_title(content)
        description = extract_description(content)
        keywords = extract_keywords(content)
        
        entries[key] = {
            'title': title,
            'type': file_type,
            'category': file_type.title(),
            'description': description,
            'keywords': keywords,
            'content': content,
            'path': str(rel_path),
            'file_size': len(content),
            'word_count': len(content.split())
        }
    
    return entries

def generate_index_html(entries):
    """Generate main index.html file"""
    total_entries = len(entries)
    categories = list(set(entry['type'] for entry in entries.values()))
    
    # Generate category counts
    category_counts = {}
    for entry in entries.values():
        cat = entry['type']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The New World Encyclopedia</title>
    
    <!-- Marked.js for markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
    
    <!-- Prism.js for syntax highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            min-height: 100vh;
            color: #e2e8f0;
        }}

        .container {{
            display: flex;
            min-height: 100vh;
            max-width: 1600px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
        }}

        /* Compact Sidebar */
        .sidebar {{
            width: 300px;
            background: rgba(30, 41, 59, 0.95);
            color: #e2e8f0;
            overflow-y: auto;
            flex-shrink: 0;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .sidebar-header {{
            padding: 20px;
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .sidebar h1 {{
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #f8fafc;
            background: linear-gradient(45deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .search-container {{
            position: relative;
            margin-bottom: 15px;
        }}

        .search-input {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #475569;
            border-radius: 8px;
            font-size: 14px;
            background: rgba(15, 23, 42, 0.8);
            color: #f8fafc;
            outline: none;
        }}

        .search-input:focus {{
            border-color: #60a5fa;
            box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
        }}

        .search-input::placeholder {{
            color: #64748b;
        }}

        .compact-tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 15px;
        }}

        .compact-tab {{
            padding: 6px 12px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            color: #cbd5e1;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}

        .compact-tab:hover, .compact-tab.active {{
            background: linear-gradient(45deg, #60a5fa, #a78bfa);
            color: white;
            border-color: #60a5fa;
        }}

        .navigation {{
            padding: 15px 0;
        }}

        .nav-section {{
            margin-bottom: 20px;
        }}

        .nav-section h3 {{
            padding: 0 20px 10px;
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 10px;
        }}

        .nav-item {{
            display: block;
            padding: 8px 20px;
            color: #cbd5e1;
            text-decoration: none;
            transition: all 0.2s ease;
            border-left: 2px solid transparent;
            font-size: 13px;
            line-height: 1.4;
            cursor: pointer;
        }}

        .nav-item:hover {{
            background: rgba(96, 165, 250, 0.1);
            color: #f8fafc;
            border-left-color: #60a5fa;
        }}

        .nav-item.active {{
            background: rgba(96, 165, 250, 0.2);
            color: #f8fafc;
            border-left-color: #60a5fa;
        }}

        .nav-item .type-badge {{
            display: inline-block;
            background: #dc2626;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 9px;
            margin-right: 8px;
            text-transform: uppercase;
        }}

        .nav-item .type-badge.historical {{ background: #dc2626; }}
        .nav-item .type-badge.foundation {{ background: #2563eb; }}
        .nav-item .type-badge.dialectic {{ background: #7c3aed; }}
        .nav-item .type-badge.technical {{ background: #059669; }}
        .nav-item .type-badge.magic {{ background: #d97706; }}
        .nav-item .type-badge.polymorphic {{ background: #be185d; }}
        .nav-item .type-badge.philosophy {{ background: #7c2d12; }}
        .nav-item .type-badge.economics {{ background: #1e40af; }}
        .nav-item .type-badge.other {{ background: #6b7280; }}

        /* Main content area */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .content-header {{
            padding: 20px 30px;
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 5;
        }}

        .content-header h1 {{
            color: #f8fafc;
            margin-bottom: 8px;
            font-size: 2em;
        }}

        .breadcrumb {{
            color: #94a3b8;
            font-size: 14px;
        }}

        .breadcrumb a {{
            color: #60a5fa;
            text-decoration: none;
        }}

        .breadcrumb a:hover {{
            text-decoration: underline;
        }}

        .content-body {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            background: rgba(15, 23, 42, 0.5);
        }}

        /* Markdown content styling */
        .markdown-content {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.9);
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            line-height: 1.8;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .markdown-content h1 {{
            color: #f8fafc;
            border-bottom: 3px solid #60a5fa;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}

        .markdown-content h2 {{
            color: #e2e8f0;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 4px solid #60a5fa;
            font-size: 1.8em;
        }}

        .markdown-content h3 {{
            color: #e2e8f0;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}

        .markdown-content h4 {{
            color: #cbd5e1;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 1.2em;
        }}

        .markdown-content p {{
            margin-bottom: 20px;
            color: #e2e8f0;
        }}

        .markdown-content ul, .markdown-content ol {{
            margin: 20px 0;
            padding-left: 30px;
        }}

        .markdown-content li {{
            margin-bottom: 10px;
            color: #e2e8f0;
        }}

        .markdown-content blockquote {{
            border-left: 4px solid #60a5fa;
            padding: 20px 25px;
            margin: 25px 0;
            background: rgba(96, 165, 250, 0.1);
            border-radius: 0 10px 10px 0;
            font-style: italic;
            color: #cbd5e1;
        }}

        .markdown-content code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #fbbf24;
        }}

        .markdown-content pre {{
            background: rgba(0, 0, 0, 0.4);
            color: #e2e8f0;
            padding: 25px;
            border-radius: 10px;
            overflow-x: auto;
            margin: 25px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .markdown-content pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        .markdown-content a {{
            color: #60a5fa;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom 0.3s ease;
        }}

        .markdown-content a:hover {{
            border-bottom-color: #60a5fa;
        }}

        .markdown-content strong {{
            color: #f8fafc;
            font-weight: bold;
        }}

        .markdown-content em {{
            color: #cbd5e1;
            font-style: italic;
        }}

        .markdown-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
        }}

        .markdown-content th, .markdown-content td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .markdown-content th {{
            background: rgba(96, 165, 250, 0.1);
            color: #f8fafc;
            font-weight: bold;
        }}

        .markdown-content hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #60a5fa, transparent);
            margin: 35px 0;
        }}

        .stats {{
            padding: 15px 20px;
            background: rgba(15, 23, 42, 0.8);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 11px;
            color: #94a3b8;
        }}

        .highlight {{
            background: linear-gradient(45deg, #fde68a, #fbbf24);
            color: #0f172a;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }}

        .welcome-message {{
            text-align: center;
            color: #94a3b8;
            font-size: 1.3em;
            margin-top: 100px;
            padding: 40px;
            background: rgba(15, 23, 42, 0.9);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* Responsive design */
        @media (max-width: 1200px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
                max-height: 400px;
            }}
            
            .compact-tabs {{
                justify-content: center;
            }}
        }}

        @media (max-width: 768px) {{
            .content-body {{
                padding: 20px;
            }}
            
            .markdown-content {{
                padding: 25px;
            }}
            
            .sidebar-header {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>The New World Encyclopedia</h1>
                <div class="search-container">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search {total_entries} entries...">
                </div>
                <div class="compact-tabs" id="categoryTabs">
                    <div class="compact-tab active" data-category="all">All ({total_entries})</div>"""
    
    # Add category tabs
    for cat in sorted(categories):
        count = category_counts[cat]
        html += f'<div class="compact-tab" data-category="{cat}">{cat.title()} ({count})</div>'
    
    html += """
                </div>
            </div>
            
            <div class="navigation" id="navigation">
                <!-- Navigation will be populated by JavaScript -->
            </div>
            
            <div class="stats" id="stats">
                <!-- Statistics will be populated by JavaScript -->
            </div>
        </div>

        <div class="main-content">
            <div class="content-header">
                <h1 id="contentTitle">The New World Encyclopedia</h1>
                <div class="breadcrumb" id="breadcrumb">A comprehensive guide to the Great Transition</div>
            </div>
            <div class="content-body">
                <div class="markdown-content" id="contentBody">
                    <div class="welcome-message">
                        <h2>Welcome to The New World Encyclopedia</h2>
                        <p>Explore the transformation from predatory systems to will-manifestation infrastructure through polymorphic crucibles, trust networks, and magical interfaces.</p>
                        <p>Choose an entry from the sidebar to begin reading.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Encyclopedia entries data
        const encyclopediaEntries = {"""
    
    # Add entries data
    for key, entry in entries.items():
        html += f"""
            "{key}": {{
                title: "{escape_js_string(entry['title'])}",
                type: "{entry['type']}",
                category: "{entry['category']}",
                description: "{escape_js_string(entry['description'])}",
                keywords: {json.dumps(entry['keywords'])},
                content: `{entry['content']}`.replace(/\\`/g, "`"),
                path: "{entry['path']}",
                file_size: {entry['file_size']},
                word_count: {entry['word_count']}
            }},"""
    
    html += """
        };

        let currentFilter = 'all';
        let currentEntry = null;

        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const categoryTabs = document.getElementById('categoryTabs');
        const navigation = document.getElementById('navigation');
        const stats = document.getElementById('stats');
        const contentTitle = document.getElementById('contentTitle');
        const breadcrumb = document.getElementById('breadcrumb');
        const contentBody = document.getElementById('contentBody');

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            renderNavigation();
            updateStats();
            
            // Search functionality
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                filterEntries(searchTerm, currentFilter);
            });
            
            // Tab functionality
            categoryTabs.addEventListener('click', function(e) {
                if (e.target.classList.contains('compact-tab')) {
                    categoryTabs.querySelectorAll('.compact-tab').forEach(tab => tab.classList.remove('active'));
                    e.target.classList.add('active');
                    currentFilter = e.target.dataset.category;
                    const searchTerm = searchInput.value.toLowerCase();
                    filterEntries(searchTerm, currentFilter);
                }
            });
        });

        function filterEntries(searchTerm, category) {
            const filteredEntries = Object.entries(encyclopediaEntries).filter(([key, entry]) => {
                const matchesSearch = searchTerm === '' || 
                    entry.title.toLowerCase().includes(searchTerm) ||
                    entry.description.toLowerCase().includes(searchTerm) ||
                    entry.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm));
                
                const matchesCategory = category === 'all' || entry.type === category;
                
                return matchesSearch && matchesCategory;
            });
            
            renderNavigation(filteredEntries);
            updateStats(filteredEntries);
        }

        function renderNavigation(entries = null) {
            const entriesToShow = entries || Object.entries(encyclopediaEntries);
            
            // Group entries by type
            const groupedEntries = {};
            entriesToShow.forEach(([key, entry]) => {
                if (!groupedEntries[entry.type]) {
                    groupedEntries[entry.type] = [];
                }
                groupedEntries[entry.type].push([key, entry]);
            });

            navigation.innerHTML = '';
            
            Object.entries(groupedEntries).forEach(([type, typeEntries]) => {
                const section = document.createElement('div');
                section.className = 'nav-section';
                
                const heading = document.createElement('h3');
                heading.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                section.appendChild(heading);
                
                typeEntries.forEach(([key, entry]) => {
                    const navItem = document.createElement('div');
                    navItem.className = 'nav-item';
                    navItem.innerHTML = `
                        <span class="type-badge ${entry.type}">${entry.type.charAt(0).toUpperCase()}</span>
                        ${entry.title}
                    `;
                    
                    navItem.addEventListener('click', () => {
                        // Remove active class from all items
                        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                        // Add active class to clicked item
                        navItem.classList.add('active');
                        // Load the entry
                        loadEntry(key, entry);
                    });
                    
                    section.appendChild(navItem);
                });
                
                navigation.appendChild(section);
            });
        }

        async function loadEntry(key, entry) {
            currentEntry = entry;
            contentTitle.textContent = entry.title;
            breadcrumb.innerHTML = `<a href="#">Encyclopedia</a> > <a href="#">${entry.category}</a> > ${entry.title}`;
            
            // Render markdown content
            const html = marked.parse(entry.content);
            contentBody.innerHTML = html;
            
            // Highlight code blocks
            if (typeof Prism !== 'undefined') {
                Prism.highlightAll();
            }
            
            // Scroll to top
            document.querySelector('.content-body').scrollTop = 0;
        }

        function updateStats(entries = null) {
            const entriesToCount = entries || Object.entries(encyclopediaEntries);
            const totalEntries = entriesToCount.length;
            const categories = [...new Set(entriesToCount.map(([key, entry]) => entry.type))];
            
            const categoryCounts = categories.map(category => {
                const count = entriesToCount.filter(([key, entry]) => entry.type === category).length;
                return `${category.charAt(0).toUpperCase()}: ${count}`;
            }).join(' | ');
            
            const totalWords = entriesToCount.reduce((sum, [key, entry]) => sum + entry.word_count, 0);
            
            stats.innerHTML = `
                <div><strong>Total Entries:</strong> ${totalEntries}</div>
                <div><strong>Total Words:</strong> ${totalWords.toLocaleString()}</div>
                <div style="margin-top: 8px; font-size: 10px;">${categoryCounts}</div>
            `;
        }
    </script>
</body>
</html>"""
    
    return html

def create_htaccess():
    """Create .htaccess file for Apache server"""
    return """# Apache configuration for The New World Encyclopedia

# Enable mod_rewrite
RewriteEngine On

# Redirect root to index.html
DirectoryIndex index.html

# Set MIME types
AddType text/html .html
AddType text/css .css
AddType application/javascript .js
AddType text/markdown .md

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript text/markdown
</IfModule>

# Set cache headers
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/html "access plus 1 hour"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>

# Error pages
ErrorDocument 404 /index.html
"""

def create_readme():
    """Create README file for deployment instructions"""
    return """# The New World Encyclopedia - Website

A comprehensive, deployable website containing all documents from the New World system.

## Quick Deployment

### Option 1: DigitalOcean/Azure/Linode
1. Create a new droplet/server
2. Install Apache: `sudo apt update && sudo apt install apache2`
3. Upload all files to `/var/www/html/`
4. Set permissions: `sudo chown -R www-data:www-data /var/www/html/`
5. Enable Apache: `sudo systemctl enable apache2 && sudo systemctl start apache2`
6. Visit your server's IP address

### Option 2: Shared Hosting (cPanel, etc.)
1. Upload all files to your `public_html` directory
2. Ensure `index.html` is in the root
3. Visit your domain

### Option 3: GitHub Pages
1. Upload to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Select source branch

## File Structure
- `index.html` - Main encyclopedia interface
- `.htaccess` - Apache configuration
- `README.md` - This file

## Features
- **Complete Offline Functionality** - All content embedded
- **Fast Search** - Real-time filtering across all documents
- **Category Filtering** - Filter by document type
- **Responsive Design** - Works on all devices
- **Markdown Rendering** - Full markdown support with syntax highlighting
- **No Database Required** - Pure HTML/CSS/JavaScript

## Content Included
- All foundation documents
- Historical entries
- Dialectical analysis
- Magic and polymorphic systems
- Economic frameworks
- Technical architecture
- And much more...

## Browser Support
- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers

## Customization
Edit `index.html` to modify:
- Colors and styling
- Add new documents
- Change layout
- Add features

Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main function to generate complete website"""
    print("Generating The New World Encyclopedia Website...")
    
    # Scan all documents
    system_share_dir = Path('../system share/system share')
    print(f"Scanning documents in: {system_share_dir}")
    
    entries = scan_documents(system_share_dir)
    print(f"Found {len(entries)} documents")
    
    # Generate main HTML file
    print("Generating index.html...")
    html_content = generate_index_html(entries)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create .htaccess file
    print("Creating .htaccess...")
    with open('.htaccess', 'w', encoding='utf-8') as f:
        f.write(create_htaccess())
    
    # Create README
    print("Creating README.md...")
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(create_readme())
    
    # Create deployment info
    deployment_info = {
        'generated_at': datetime.now().isoformat(),
        'total_documents': len(entries),
        'categories': list(set(entry['type'] for entry in entries.values())),
        'total_words': sum(entry['word_count'] for entry in entries.values()),
        'total_size': sum(entry['file_size'] for entry in entries.values())
    }
    
    with open('deployment_info.json', 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n✅ Website generated successfully!")
    print(f"📁 Location: {Path.cwd()}")
    print(f"📄 Documents: {len(entries)}")
    print(f"📊 Categories: {len(deployment_info['categories'])}")
    print(f"📝 Total words: {deployment_info['total_words']:,}")
    print(f"💾 Total size: {deployment_info['total_size']:,} bytes")
    print(f"\n🚀 Ready for deployment!")
    print(f"   Just upload all files to your web server and visit index.html")

if __name__ == "__main__":
    main()