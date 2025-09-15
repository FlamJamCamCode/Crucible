#!/usr/bin/env python3
"""
Generate a static encyclopedia viewer that embeds all markdown content directly.
No server required - just open the HTML file in a browser.
"""

import os
import json
from pathlib import Path

def read_markdown_file(file_path):
    """Read a markdown file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def get_document_structure():
    """Return the document structure with all files."""
    return {
        'foundations': [
            {'id': 'exec_summary', 'file': '1 exec_summary_vision.md', 'title': '1. Executive Summary & Vision'},
            {'id': 'foundational_mechanisms', 'file': '2 foundational_mechanisms.md', 'title': '2. Foundational Mechanisms'},
            {'id': 'technical_architecture', 'file': '3 technical_architecture.md', 'title': '3. Technical Architecture'},
            {'id': 'blob_classes', 'file': '4 blob_classes_discovery.md', 'title': '4. Blob Classes Discovery'},
            {'id': 'language_evolution', 'file': '5 language_evolution_system.md', 'title': '5. Language Evolution System'},
            {'id': 'cohesionnet', 'file': '6 cohesionnet_use_case.md', 'title': '6. CohesionNet Use Case'},
            {'id': 'health_system', 'file': '7 health_system_transformation.md', 'title': '7. Health System Transformation'},
            {'id': 'computational_utility', 'file': '8 computational_utility_networks.md', 'title': '8. Computational Utility Networks'},
            {'id': 'electricity_routing', 'file': '9 electricity_routing_markets.md', 'title': '9. Electricity Routing Markets'},
            {'id': 'water_supply', 'file': '10 water_supply_trust.md', 'title': '10. Water Supply Trust'},
            {'id': 'food_systems', 'file': '11 food_systems_revolution.md', 'title': '11. Food Systems Revolution'},
            {'id': 'will_coalescence', 'file': '12 will_coalescence_meta_utility.md', 'title': '12. Will Coalescence Meta Utility'},
            {'id': 'markets_value', 'file': '13 markets_value_discovery.md', 'title': '13. Markets Value Discovery'},
            {'id': 'civilizational_emergence', 'file': '14 civilizational_emergence.md', 'title': '14. Civilizational Emergence'},
            {'id': 'will_manifestation', 'file': '15 will_manifestation_philosophy.md', 'title': '15. Will Manifestation Philosophy'},
            {'id': 'kant_insights', 'file': '15b_kant_insights_manifesto.md', 'title': '15b. Kant Insights Manifesto'},
            {'id': 'daemonic_architecture', 'file': '16 daemonic_architecture.md', 'title': '16. Daemonic Architecture'},
            {'id': 'crucible_sovereignty', 'file': '17 crucible_sovereignty_system.md', 'title': '17. Crucible Sovereignty System'},
            {'id': 'vocabulary_concepts', 'file': '18 vocabulary_concepts_guide.md', 'title': '18. Vocabulary & Concepts Guide'},
            {'id': 'implementation_roadmap', 'file': '19 implementation_roadmap.md', 'title': '19. Implementation Roadmap'},
            {'id': 'trust_network', 'file': '20 trust_network_dynamics.md', 'title': '20. Trust Network Dynamics'},
            {'id': 'ar_phase_engine', 'file': '21 ar_phase_engine_specs.md', 'title': '21. AR Phase Engine Specs'},
            {'id': 'system_integration', 'file': '22 system_integration_synthesis.md', 'title': '22. System Integration Synthesis'},
            {'id': 'heidegger_thrownness', 'file': '23 heidegger_thrownness_terraforming.md', 'title': '23. Heidegger Thrownness Terraforming'},
            {'id': 'nss', 'file': '24 nss.md', 'title': '24. NSS'},
            {'id': 'capital_illusion', 'file': '24a capital-illusion-dissolution.md', 'title': '24a. Capital Illusion Dissolution'},
            {'id': 'employment', 'file': '24b employment.md', 'title': '24b. Employment'},
            {'id': 'subjective_economics', 'file': '24c tentative-bastards-subjective-economics.md', 'title': '24c. Tentative Bastards Subjective Economics'},
            {'id': 'natural_selection_capital', 'file': '24d natural-selection-vs-capital.md', 'title': '24d. Natural Selection vs Capital'},
            {'id': 'nss_money', 'file': '24e nss-money-exposition.md', 'title': '24e. NSS Money Exposition'},
            {'id': 'will_economic_task', 'file': '24f will-economic-task-system.md', 'title': '24f. Will Economic Task System'},
            {'id': 'discovery_os', 'file': '25 discovery-os-expanded-into-broader-picture.md', 'title': '25. Discovery OS Expanded'},
            {'id': 'crucible_discovery', 'file': '26. crucible-discovery-synthesis.md', 'title': '26. Crucible Discovery Synthesis'},
            {'id': 'sovereign_crucible', 'file': '27. The Sovereign Crucible and the Might Is Right Alliance -- A Framework for Will-Based Civilizations.md', 'title': '27. The Sovereign Crucible'},
            {'id': 'metagame_dynamics', 'file': '28 Metagame of World Dynamics.md', 'title': '28. Metagame of World Dynamics'},
            {'id': 'cause_effect_might', 'file': '29. cause-and-effect-might-with-right.md', 'title': '29. Cause and Effect Might with Right'},
            {'id': 'gradient_will_solving', 'file': '29a. gradient-of-will-solving-systems.md', 'title': '29a. Gradient of Will Solving Systems'},
            {'id': 'neologistic_reality', 'file': '30. neologistic-reality-cutting.md', 'title': '30. Neologistic Reality Cutting'},
            {'id': 'aiddaemonic_semantic', 'file': '31. aiddaemonic-semantic-bridging.md', 'title': '31. Aiddaemonic Semantic Bridging'},
            {'id': 'neo_colonialism', 'file': '32. neo-colonialism.md', 'title': '32. Neo-Colonialism'},
            {'id': 'removal_men_fascism', 'file': '34. Removal of Men by force under cover of fascism.md', 'title': '34. Removal of Men by Force under Cover of Fascism'},
            {'id': 'living_new_world', 'file': '35. living-in-new-world.md', 'title': '35. Living in New World'},
            {'id': 'worst_illuminated', 'file': '76. The Worst Illuminated.md', 'title': '76. The Worst Illuminated'},
            {'id': 'critique_west', 'file': 'a_critique_of_the_west.md', 'title': 'A Critique of The West'},
            {'id': 'routing_symbols', 'file': 'Appendix_A_Routing_Symbols_Comprehensive.md', 'title': 'Appendix A: Routing Symbols Comprehensive'}
        ],
        'historical': [
            {'id': 'new_world_genesis', 'file': 'new-world-genesis-gpt5.md', 'title': 'New World Genesis (GPT-5)'},
            {'id': 'terraformer_bootstrap', 'file': 'terraformer-bootstrap-gpt5.md', 'title': 'The Terraformer Bootstrap (GPT-5)'},
            {'id': 'neo_colonial_alliance', 'file': 'neo-colonial-alliance-gpt5.md', 'title': 'The Neo-Colonial Alliance (GPT-5)'},
            {'id': 'great_fork', 'file': 'great-fork-gpt5.md', 'title': 'The Great Fork (GPT-5)'},
            {'id': 'new_world_genesis_orig', 'file': 'new-world-genesis.md', 'title': 'New World Genesis (Original)'},
            {'id': 'terraformer_bootstrap_orig', 'file': 'terraformer-bootstrap.md', 'title': 'The Terraformer Bootstrap (Original)'},
            {'id': 'neo_colonial_alliance_orig', 'file': 'neo-colonial-alliance.md', 'title': 'The Neo-Colonial Alliance (Original)'},
            {'id': 'great_fork_orig', 'file': 'great-fork.md', 'title': 'The Great Fork (Original)'}
        ]
    }

def generate_static_html():
    """Generate the static HTML file with all content embedded."""
    
    # Get document structure
    doc_structure = get_document_structure()
    
    # Load all documents
    documents = {}
    base_path = Path("system share")
    
    for category, docs in doc_structure.items():
        documents[category] = {}
        for doc in docs:
            file_path = base_path / category / doc['file']
            content = read_markdown_file(file_path)
            documents[category][doc['id']] = {
                'title': doc['title'],
                'content': content,
                'filename': doc['file']
            }
    
    # Generate the HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Encyclopedia Reader - Foundations & Historical Entries</title>
    
    <!-- Marker.js for enhanced reading experience -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@markerjs/markerjs3@latest/dist/markerjs3.css">
    <script src="https://cdn.jsdelivr.net/npm/@markerjs/markerjs3@latest/dist/markerjs3.umd.js"></script>
    
    <!-- Marked.js for markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
    
    <!-- Prism.js for syntax highlighting -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css">
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}

        .container {{
            display: flex;
            min-height: 100vh;
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.1);
        }}

        /* Sidebar */
        .sidebar {{
            width: 300px;
            background: #2c3e50;
            color: white;
            overflow-y: auto;
            flex-shrink: 0;
        }}

        .sidebar-header {{
            padding: 20px;
            background: #34495e;
            border-bottom: 1px solid #4a5f7a;
        }}

        .sidebar h1 {{
            font-size: 1.2em;
            margin-bottom: 10px;
        }}

        .search-container {{
            position: relative;
        }}

        .search-input {{
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            background: white;
            color: #333;
        }}

        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 5px 5px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }}

        .search-result {{
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            color: #333;
        }}

        .search-result:hover {{
            background: #f0f0f0;
        }}

        .search-result:last-child {{
            border-bottom: none;
        }}

        .search-result .title {{
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .search-result .excerpt {{
            font-size: 12px;
            color: #666;
        }}

        .navigation {{
            padding: 20px 0;
        }}

        .nav-section {{
            margin-bottom: 20px;
        }}

        .nav-section h3 {{
            padding: 0 20px 10px;
            color: #ecf0f1;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #4a5f7a;
            margin-bottom: 10px;
        }}

        .nav-item {{
            display: block;
            padding: 8px 20px;
            color: #bdc3c7;
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }}

        .nav-item:hover {{
            background: #34495e;
            color: white;
            border-left-color: #3498db;
        }}

        .nav-item.active {{
            background: #3498db;
            color: white;
            border-left-color: #2980b9;
        }}

        /* Main content area */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .content-header {{
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #eee;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .content-header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .breadcrumb {{
            color: #7f8c8d;
            font-size: 14px;
        }}

        .breadcrumb a {{
            color: #3498db;
            text-decoration: none;
        }}

        .breadcrumb a:hover {{
            text-decoration: underline;
        }}

        .content-body {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            background: #fafafa;
        }}

        /* Markdown content styling */
        .markdown-content {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            line-height: 1.7;
        }}

        .markdown-content h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}

        .markdown-content h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}

        .markdown-content h3 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        .markdown-content p {{
            margin-bottom: 20px;
            color: #444;
        }}

        .markdown-content ul, .markdown-content ol {{
            margin: 20px 0;
            padding-left: 30px;
        }}

        .markdown-content li {{
            margin-bottom: 8px;
        }}

        .markdown-content blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #555;
        }}

        .markdown-content code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}

        .markdown-content pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }}

        .markdown-content pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        .markdown-content a {{
            color: #3498db;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom 0.3s ease;
        }}

        .markdown-content a:hover {{
            border-bottom-color: #3498db;
        }}

        .markdown-content a.internal-link {{
            background: #e8f4fd;
            padding: 2px 6px;
            border-radius: 3px;
            border-bottom: none;
        }}

        .markdown-content a.internal-link:hover {{
            background: #d1ecf1;
        }}

        /* Concept tooltips */
        .concept {{
            position: relative;
            cursor: help;
            border-bottom: 2px dotted #3498db;
            color: #2980b9;
        }}

        .concept-tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            max-width: 300px;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            pointer-events: none;
        }}

        .concept-tooltip::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #2c3e50;
        }}

        .concept:hover .concept-tooltip {{
            opacity: 1;
            visibility: visible;
        }}

        /* Loading states */
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            color: #7f8c8d;
        }}

        .loading::after {{
            content: '';
            width: 20px;
            height: 20px;
            border: 2px solid #ddd;
            border-top-color: #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* Mobile responsiveness */
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                max-height: 300px;
            }}
            
            .content-body {{
                padding: 20px;
            }}
            
            .markdown-content {{
                padding: 20px;
            }}
        }}

        /* Marker.js customization */
        .markerjs-editor {{
            z-index: 10000 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>Static Encyclopedia Reader</h1>
                <div class="search-container">
                    <input type="text" class="search-input" placeholder="Search all documents..." id="searchInput">
                    <div class="search-results" id="searchResults"></div>
                </div>
            </div>
            
            <nav class="navigation">
                <div class="nav-section">
                    <h3>Foundations</h3>
                    <div id="foundationsNav"></div>
                </div>
                
                <div class="nav-section">
                    <h3>Historical Entries</h3>
                    <div id="historicalNav"></div>
                </div>
            </nav>
        </div>

        <!-- Main content -->
        <div class="main-content">
            <div class="content-header">
                <div class="breadcrumb" id="breadcrumb">
                    <a href="#" onclick="loadHome()">Home</a>
                </div>
                <h1 id="contentTitle">Welcome to the Encyclopedia</h1>
            </div>
            
            <div class="content-body">
                <div id="contentArea">
                    <div class="markdown-content">
                        <h1>Welcome to the Static Encyclopedia Reader</h1>
                        <p>This reader provides access to the foundational documents and historical entries of the system. All content is embedded directly in this file - no server required!</p>
                        
                        <h2>Features</h2>
                        <ul>
                            <li><strong>Enhanced Reading:</strong> Use Marker.js to annotate and highlight important passages</li>
                            <li><strong>Smart Search:</strong> Search across all documents with instant results</li>
                            <li><strong>Concept Hover:</strong> Hover over highlighted concepts for definitions</li>
                            <li><strong>Navigation:</strong> Click any internal link to jump to related documents</li>
                            <li><strong>Browser History:</strong> Full back/forward support with state preservation</li>
                            <li><strong>No Server Required:</strong> Everything is embedded in this single file</li>
                        </ul>
                        
                        <h2>Getting Started</h2>
                        <p>Select a document from the navigation menu to begin reading. You can use the search function to quickly find topics of interest across all documents.</p>
                        
                        <h2>Document Statistics</h2>
                        <ul>
                            <li><strong>Foundations:</strong> {len(documents['foundations'])} documents</li>
                            <li><strong>Historical Entries:</strong> {len(documents['historical'])} documents</li>
                            <li><strong>Total:</strong> {len(documents['foundations']) + len(documents['historical'])} documents</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Embedded document data
        const documents = {json.dumps(documents, indent=8)};
        
        // Global state management
        const appState = {{
            currentDocument: null,
            historyStack: [],
            historyIndex: -1
        }};

        // Document structure for navigation
        const documentStructure = {json.dumps(doc_structure, indent=8)};

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {{
            initializeApp();
        }});

        function initializeApp() {{
            buildNavigation();
            setupSearch();
            setupHistoryAPI();
            updateBreadcrumb();
        }}

        function buildNavigation() {{
            const foundationsNav = document.getElementById('foundationsNav');
            const historicalNav = document.getElementById('historicalNav');

            // Build foundations navigation
            documentStructure.foundations.forEach(doc => {{
                const link = document.createElement('a');
                link.href = '#';
                link.className = 'nav-item';
                link.textContent = doc.title;
                link.onclick = (e) => {{
                    e.preventDefault();
                    loadDocument('foundations', doc.id, doc.title);
                }};
                foundationsNav.appendChild(link);
            }});

            // Build historical navigation
            documentStructure.historical.forEach(doc => {{
                const link = document.createElement('a');
                link.href = '#';
                link.className = 'nav-item';
                link.textContent = doc.title;
                link.onclick = (e) => {{
                    e.preventDefault();
                    loadDocument('historical', doc.id, doc.title);
                }};
                historicalNav.appendChild(link);
            }});
        }}

        function setupSearch() {{
            const searchInput = document.getElementById('searchInput');
            const searchResults = document.getElementById('searchResults');

            searchInput.addEventListener('input', function() {{
                const query = this.value.trim();
                if (query.length < 2) {{
                    searchResults.style.display = 'none';
                    return;
                }}

                performSearch(query);
            }});

            // Hide search results when clicking outside
            document.addEventListener('click', function(e) {{
                if (!e.target.closest('.search-container')) {{
                    searchResults.style.display = 'none';
                }}
            }});
        }}

        function performSearch(query) {{
            const searchResults = document.getElementById('searchResults');
            searchResults.innerHTML = '<div class="search-result">Searching...</div>';
            searchResults.style.display = 'block';

            const results = searchDocuments(query);
            displaySearchResults(results);
        }}

        function searchDocuments(query) {{
            const results = [];
            const lowercaseQuery = query.toLowerCase();

            // Search through all documents
            for (const [category, docs] of Object.entries(documents)) {{
                for (const [docId, docData] of Object.entries(docs)) {{
                    const content = docData.content.toLowerCase();
                    if (content.includes(lowercaseQuery)) {{
                        const lines = docData.content.split('\\n');
                        const matchingLines = lines.filter(line => 
                            line.toLowerCase().includes(lowercaseQuery)
                        );

                        if (matchingLines.length > 0) {{
                            results.push({{
                                category: category,
                                docId: docId,
                                title: docData.title,
                                matches: matchingLines.slice(0, 3),
                                totalMatches: matchingLines.length
                            }});
                        }}
                    }}
                }}
            }}

            return results.slice(0, 10); // Limit to 10 results
        }}

        function displaySearchResults(results) {{
            const searchResults = document.getElementById('searchResults');
            
            if (results.length === 0) {{
                searchResults.innerHTML = '<div class="search-result">No results found</div>';
                return;
            }}

            searchResults.innerHTML = results.map(result => {{
                const excerpt = result.matches[0].substring(0, 100) + '...';
                return `
                    <div class="search-result" onclick="loadDocument('${{result.category}}', '${{result.docId}}', '${{result.title}}')">
                        <div class="title">${{result.title}}</div>
                        <div class="excerpt">${{excerpt}}</div>
                        <div class="excerpt">${{result.totalMatches}} matches</div>
                    </div>
                `;
            }}).join('');
        }}

        function loadDocument(category, docId, title) {{
            const contentArea = document.getElementById('contentArea');
            const contentTitle = document.getElementById('contentTitle');
            
            const docData = documents[category][docId];
            if (!docData) {{
                contentArea.innerHTML = `
                    <div class="markdown-content">
                        <h1>Document Not Found</h1>
                        <p>Could not find document: ${{docId}}</p>
                    </div>
                `;
                return;
            }}

            const html = marked.parse(docData.content);
            
            contentArea.innerHTML = `
                <div class="markdown-content" id="markdownContent">
                    ${{html}}
                </div>
            `;
            
            contentTitle.textContent = title;
            
            // Update navigation active state
            updateActiveNavigation(docId);
            
            // Process internal links
            processInternalLinks();
            
            // Add concept tooltips
            addConceptTooltips();
            
            // Initialize Marker.js
            initializeMarker();
            
            // Update browser history
            updateHistory(category, docId, title);
            
            // Update breadcrumb
            updateBreadcrumb(category, title);
            
            appState.currentDocument = {{ category, docId, title }};
        }}

        function updateActiveNavigation(docId) {{
            // Remove active class from all nav items
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Add active class to current document
            const currentNavItem = Array.from(document.querySelectorAll('.nav-item')).find(item => 
                item.textContent.includes(docId.replace(/_/g, ' ')) || 
                item.textContent.toLowerCase().includes(docId.toLowerCase())
            );
            
            if (currentNavItem) {{
                currentNavItem.classList.add('active');
            }}
        }}

        function processInternalLinks() {{
            const markdownContent = document.getElementById('markdownContent');
            if (!markdownContent) return;

            const links = markdownContent.querySelectorAll('a[href$=".md"]');
            links.forEach(link => {{
                link.classList.add('internal-link');
                link.onclick = function(e) {{
                    e.preventDefault();
                    const href = this.getAttribute('href');
                    const filename = href.split('/').pop();
                    
                    // Try to find the document in both categories
                    let foundDoc = null;
                    let category = null;
                    
                    // Check foundations
                    foundDoc = documentStructure.foundations.find(doc => doc.file === filename);
                    if (foundDoc) {{
                        category = 'foundations';
                    }} else {{
                        // Check historical
                        foundDoc = documentStructure.historical.find(doc => doc.file === filename);
                        if (foundDoc) {{
                            category = 'historical';
                        }}
                    }}
                    
                    if (foundDoc && category) {{
                        // Find the doc ID from the documents object
                        const docId = Object.keys(documents[category]).find(id => 
                            documents[category][id].filename === filename
                        );
                        if (docId) {{
                            loadDocument(category, docId, foundDoc.title);
                        }}
                    }} else {{
                        console.warn('Could not find document:', filename);
                        alert(`Could not find document: ${{filename}}`);
                    }}
                }};
            }});
        }}

        function addConceptTooltips() {{
            const markdownContent = document.getElementById('markdownContent');
            if (!markdownContent) return;

            // Add tooltips to concept terms
            const conceptTerms = [
                'Proof of Person', 'PoP', 'Proof of Utility', 'PoU', 'Trust Networks',
                'Discovery OS', 'Blob Classes', 'AR Phase Engine', 'Will Coalescence',
                'Aiddaemon', 'The Crucible', 'Daemonia', '1234X4321 Axis', 'Triad',
                'Sovereignty', 'Halo', 'Substratum', 'Polymorphic Crucible', 'NSS'
            ];

            conceptTerms.forEach(term => {{
                const regex = new RegExp(`\\\\b(${{term.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&')}})\\\\b`, 'gi');
                const walker = document.createTreeWalker(
                    markdownContent,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                const textNodes = [];
                let node;
                while (node = walker.nextNode()) {{
                    if (node.textContent.match(regex)) {{
                        textNodes.push(node);
                    }}
                }}

                textNodes.forEach(textNode => {{
                    const parent = textNode.parentNode;
                    if (parent.tagName === 'CODE' || parent.tagName === 'PRE') return;

                    const html = textNode.textContent.replace(regex, (match) => {{
                        const definition = getConceptDefinition(match);
                        if (definition) {{
                            return `<span class="concept">${{match}}<div class="concept-tooltip">${{definition}}</div></span>`;
                        }}
                        return match;
                    }});

                    if (html !== textNode.textContent) {{
                        const wrapper = document.createElement('span');
                        wrapper.innerHTML = html;
                        parent.replaceChild(wrapper, textNode);
                    }}
                }});
            }});
        }}

        function getConceptDefinition(term) {{
            const definitions = {{
                'Proof of Person': 'Verification that a pseudonym represents a real human through accumulated witness testimony, without revealing identity.',
                'PoP': 'Verification that a pseudonym represents a real human through accumulated witness testimony, without revealing identity.',
                'Proof of Utility': 'Real persons with PoP confirming actual value delivery, creating ungameable verification of utility provision.',
                'PoU': 'Real persons with PoP confirming actual value delivery, creating ungameable verification of utility provision.',
                'Trust Networks': 'Information conduits that eliminate defensive overhead while enabling collective intelligence.',
                'Discovery OS': 'Systems that build themselves by discovering actual capabilities rather than assuming them.',
                'Blob Classes': 'Neural network compressed representations that handle combinatorial explosion by learning patterns rather than categorizing.',
                'AR Phase Engine': 'A system foundation that makes will pathways visible as navigable possibilities.',
                'Will Coalescence': 'The alignment of multiple wills toward compatible expression.',
                'Aiddaemon': 'Personal AI surrogate that tries to emulate your daemon (deep will pattern).',
                'The Crucible': 'Testing ground for new sovereignties and the overall domination-replacement-system.',
                'Daemonia': 'Sovereign moral/spiritual worlds created around unifying will and daemon.',
                'Triad': 'Structure consisting of Sovereignty (Authority/Command), Halo (Philosophy/Law), Substratum (People/Material).',
                'NSS': 'Natural Selection System - performance-based stewardship system.'
            }};
            return definitions[term];
        }}

        function initializeMarker() {{
            const markdownContent = document.getElementById('markdownContent');
            if (!markdownContent) return;

            // Initialize Marker.js on the content
            const markerArea = new MarkerArea(markdownContent);
            
            // Add marker button to the content header
            const contentHeader = document.querySelector('.content-header');
            let markerButton = document.getElementById('markerButton');
            
            if (!markerButton) {{
                markerButton = document.createElement('button');
                markerButton.id = 'markerButton';
                markerButton.textContent = 'Add Annotation';
                markerButton.style.cssText = `
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: 10px;
                `;
                markerButton.onclick = () => markerArea.show();
                contentHeader.appendChild(markerButton);
            }}
        }}

        function setupHistoryAPI() {{
            // Handle browser back/forward
            window.addEventListener('popstate', function(event) {{
                if (event.state && event.state.document) {{
                    const {{ category, docId, title }} = event.state.document;
                    loadDocument(category, docId, title);
                }} else {{
                    loadHome();
                }}
            }});
        }}

        function updateHistory(category, docId, title) {{
            const state = {{
                document: {{ category, docId, title }},
                timestamp: Date.now()
            }};
            
            history.pushState(state, title, `#${{category}}/${{docId}}`);
        }}

        function loadHome() {{
            const contentArea = document.getElementById('contentArea');
            const contentTitle = document.getElementById('contentTitle');
            
            contentArea.innerHTML = `
                <div class="markdown-content">
                    <h1>Welcome to the Static Encyclopedia Reader</h1>
                    <p>This reader provides access to the foundational documents and historical entries of the system. All content is embedded directly in this file - no server required!</p>
                    
                    <h2>Features</h2>
                    <ul>
                        <li><strong>Enhanced Reading:</strong> Use Marker.js to annotate and highlight important passages</li>
                        <li><strong>Smart Search:</strong> Search across all documents with instant results</li>
                        <li><strong>Concept Hover:</strong> Hover over highlighted concepts for definitions</li>
                        <li><strong>Navigation:</strong> Click any internal link to jump to related documents</li>
                        <li><strong>Browser History:</strong> Full back/forward support with state preservation</li>
                        <li><strong>No Server Required:</strong> Everything is embedded in this single file</li>
                    </ul>
                    
                    <h2>Getting Started</h2>
                    <p>Select a document from the navigation menu to begin reading. You can use the search function to quickly find topics of interest across all documents.</p>
                    
                    <h2>Document Statistics</h2>
                    <ul>
                        <li><strong>Foundations:</strong> {len(documents['foundations'])} documents</li>
                        <li><strong>Historical Entries:</strong> {len(documents['historical'])} documents</li>
                        <li><strong>Total:</strong> {len(documents['foundations']) + len(documents['historical'])} documents</li>
                    </ul>
                </div>
            `;
            
            contentTitle.textContent = 'Welcome to the Encyclopedia';
            
            // Remove active navigation
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Update breadcrumb
            updateBreadcrumb();
            
            // Update history
            history.pushState(null, 'Static Encyclopedia Reader', '#');
        }}

        function updateBreadcrumb(category = null, title = null) {{
            const breadcrumb = document.getElementById('breadcrumb');
            
            if (category && title) {{
                breadcrumb.innerHTML = `
                    <a href="#" onclick="loadHome()">Home</a> > 
                    <a href="#" onclick="loadHome()">${{category.charAt(0).toUpperCase() + category.slice(1)}}</a> > 
                    ${{title}}
                `;
            }} else {{
                breadcrumb.innerHTML = '<a href="#" onclick="loadHome()">Home</a>';
            }}
        }}
    </script>
</body>
</html>"""

    return html_content

def main():
    """Main function to generate the static HTML file."""
    print("Generating static encyclopedia reader...")
    
    # Generate the HTML content
    html_content = generate_static_html()
    
    # Write to file
    output_path = Path("system share/document-viewer.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Static encyclopedia reader generated: {output_path}")
    print(f"File size: {len(html_content):,} characters")
    print(f"You can now open {output_path} directly in your browser - no server required!")

if __name__ == "__main__":
    main()
