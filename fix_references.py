#!/usr/bin/env python3
"""
Script to fix "See [document]" references in markdown files by converting them to proper hyperlinks.
This script will:
1. Find all "See [document]" patterns
2. Map document names to actual file paths
3. Convert references to markdown hyperlinks
4. Handle duplicate content by creating cross-references
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Set

class ReferenceFixer:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.document_map = {}
        self.reference_patterns = []
        self.duplicate_content = {}
        
    def build_document_map(self):
        """Build a mapping of document names to file paths"""
        print("Building document map...")
        
        # Common patterns for document references
        patterns = [
            r'(\d+)\s*\.?\s*([A-Za-z\s\-_]+)',  # "12. Will-Coalescence" -> "12 will_coalescence_meta_utility.md"
            r'([A-Za-z\s\-_]+(?:\s+System|\s+Philosophy|\s+Architecture|\s+OS|\s+Network|\s+Protocol))',  # "Trust Networks", "Discovery OS"
            r'([A-Za-z\s\-_]+(?:\s+Whitepaper|\s+Document|\s+Analysis|\s+Guide))',  # "NSS Whitepaper", "Vocabulary Guide"
        ]
        
        # Scan all markdown files
        md_files = list(self.workspace_path.rglob("*.md"))
        
        for file_path in md_files:
            file_name = file_path.stem
            file_path_str = str(file_path.relative_to(self.workspace_path))
            
            # Add exact filename match
            self.document_map[file_name] = file_path_str
            
            # Add variations
            clean_name = re.sub(r'[_\-\s]+', ' ', file_name)
            self.document_map[clean_name] = file_path_str
            
            # Add numbered versions
            for pattern in patterns:
                matches = re.findall(pattern, file_name)
                for match in matches:
                    if isinstance(match, tuple):
                        key = ' '.join(match).strip()
                    else:
                        key = match.strip()
                    self.document_map[key] = file_path_str
        
        print(f"Found {len(self.document_map)} document mappings")
        
    def find_references(self):
        """Find all 'See [document]' references in the workspace"""
        print("Finding references...")
        
        # Pattern to match "See [document]" references
        see_patterns = [
            r'\(See\s+([^)]+)\)',  # (See NSS for details)
            r'See\s+([A-Za-z\s\-_]+(?:\s+[A-Za-z\s\-_]+)*)',  # See NSS Whitepaper
            r'See\s+(\d+\.\s*[A-Za-z\s\-_]+)',  # See 12. Will-Coalescence
            r'For\s+[^,]*,\s*see\s+([^.]*)',  # For details, see Trust Networks
        ]
        
        references = []
        
        for md_file in self.workspace_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in see_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        doc_ref = match.group(1).strip()
                        references.append({
                            'file': str(md_file.relative_to(self.workspace_path)),
                            'line': content[:match.start()].count('\n') + 1,
                            'match': match.group(0),
                            'document': doc_ref,
                            'full_match': match.group(0)
                        })
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
                
        self.reference_patterns = references
        print(f"Found {len(references)} references")
        return references
    
    def find_duplicate_content(self):
        """Find duplicate content across documents"""
        print("Finding duplicate content...")
        
        # This is a simplified approach - in practice you might want more sophisticated duplicate detection
        content_hashes = {}
        
        for md_file in self.workspace_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple hash of content (you might want more sophisticated duplicate detection)
                content_hash = hash(content.strip())
                if content_hash in content_hashes:
                    if content_hash not in self.duplicate_content:
                        self.duplicate_content[content_hash] = []
                    self.duplicate_content[content_hash].append(str(md_file.relative_to(self.workspace_path)))
                else:
                    content_hashes[content_hash] = str(md_file.relative_to(self.workspace_path))
                    
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        print(f"Found {len(self.duplicate_content)} duplicate content groups")
    
    def fix_references(self):
        """Fix all references by converting them to hyperlinks"""
        print("Fixing references...")
        
        fixed_count = 0
        
        for ref in self.reference_patterns:
            file_path = self.workspace_path / ref['file']
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find the best matching document
                best_match = self.find_best_document_match(ref['document'])
                
                if best_match:
                    # Create the hyperlink
                    link_text = ref['document']
                    link_path = best_match
                    
                    # Convert to relative path if possible
                    if link_path.startswith('foundations/'):
                        link_path = f"../{link_path}"
                    elif link_path.startswith('mira/'):
                        link_path = f"../{link_path}"
                    elif link_path.startswith('controversials/'):
                        link_path = f"../{link_path}"
                    
                    new_reference = f"[{link_text}]({link_path})"
                    
                    # Replace the old reference
                    if ref['match'].startswith('(See '):
                        new_text = f"({new_reference})"
                    elif ref['match'].startswith('See '):
                        new_text = new_reference
                    elif ref['match'].startswith('For '):
                        new_text = ref['match'].replace(ref['document'], new_reference)
                    else:
                        new_text = new_reference
                    
                    # Replace in content
                    content = content.replace(ref['full_match'], new_text)
                    
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixed_count += 1
                    print(f"Fixed reference in {ref['file']}: {ref['document']} -> {link_path}")
                
            except Exception as e:
                print(f"Error fixing reference in {ref['file']}: {e}")
        
        print(f"Fixed {fixed_count} references")
    
    def find_best_document_match(self, doc_ref: str) -> str:
        """Find the best matching document for a reference"""
        doc_ref_lower = doc_ref.lower()
        
        # Try exact match first
        if doc_ref in self.document_map:
            return self.document_map[doc_ref]
        
        # Try partial matches
        best_match = None
        best_score = 0
        
        for doc_name, doc_path in self.document_map.items():
            doc_name_lower = doc_name.lower()
            
            # Calculate similarity score
            score = 0
            
            # Exact word matches
            ref_words = set(doc_ref_lower.split())
            doc_words = set(doc_name_lower.split())
            common_words = ref_words.intersection(doc_words)
            score += len(common_words) * 2
            
            # Substring matches
            if doc_ref_lower in doc_name_lower or doc_name_lower in doc_ref_lower:
                score += 3
            
            # Acronym matches (e.g., "NSS" in "nss.md")
            if len(doc_ref) <= 5 and doc_ref.isupper():
                if doc_name_lower.replace(' ', '').startswith(doc_ref.lower()):
                    score += 5
            
            if score > best_score:
                best_score = score
                best_match = doc_path
        
        return best_match if best_score > 1 else None
    
    def generate_report(self):
        """Generate a report of all findings"""
        report_file = self.workspace_path / "reference_fix_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Reference Fix Report\n\n")
            
            f.write("## Document Mappings\n\n")
            for doc_name, doc_path in sorted(self.document_map.items()):
                f.write(f"- **{doc_name}** → `{doc_path}`\n")
            
            f.write("\n## References Found\n\n")
            for ref in self.reference_patterns:
                f.write(f"- **{ref['file']}** (line {ref['line']}): {ref['match']}\n")
            
            f.write("\n## Duplicate Content\n\n")
            for content_hash, files in self.duplicate_content.items():
                f.write(f"- **Group {content_hash}**:\n")
                for file_path in files:
                    f.write(f"  - `{file_path}`\n")
        
        print(f"Report generated: {report_file}")
    
    def run(self):
        """Run the complete reference fixing process"""
        print("Starting reference fixing process...")
        
        self.build_document_map()
        self.find_references()
        self.find_duplicate_content()
        self.fix_references()
        self.generate_report()
        
        print("Reference fixing complete!")

if __name__ == "__main__":
    # Get the current workspace path
    workspace_path = os.getcwd()
    
    fixer = ReferenceFixer(workspace_path)
    fixer.run()
