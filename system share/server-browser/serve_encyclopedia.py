#!/usr/bin/env python3
"""
Simple HTTP server to serve the encyclopedia reader and markdown files.
Run this script and then open http://localhost:8000/encyclopedia-reader.html
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class EncyclopediaHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Handle markdown files with proper MIME type
        if self.path.endswith('.md'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/markdown; charset=utf-8')
            self.end_headers()
            
            file_path = self.path.lstrip('/')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'File not found')
        else:
            # Handle all other requests normally
            super().do_GET()

def main():
    port = 8000
    
    # Change to the parent directory to serve from system share root
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    os.chdir(parent_dir)
    
    print(f"Starting encyclopedia server on port {port}")
    print(f"Serving from: {parent_dir}")
    print(f"Open: http://localhost:{port}/server-browser/encyclopedia-reader.html")
    print("Press Ctrl+C to stop the server")
    
    try:
        with socketserver.TCPServer(("", port), EncyclopediaHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {port} is already in use. Try a different port:")
            print(f"python {__file__} --port 8001")
        else:
            print(f"Error starting server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        try:
            port = int(sys.argv[2])
        except (IndexError, ValueError):
            port = 8000
    else:
        port = 8000
    
    main()
