#!/usr/bin/env python3
import http.server
import socketserver
import os
import time
import threading
import json
from pathlib import Path
import urllib.parse

ROOT = Path(__file__).parent.resolve()
PUBLIC = ROOT / 'system share'
BROWSER = ROOT / 'encyclopedia-browser-gpt5.html'
BUNDLE_OUT = ROOT / 'encyclopedia-bundle-gpt5.html'
TOURS_DIR = ROOT / 'tours'
BUNDLE_PUBLIC = PUBLIC / 'encyclopedia-bundle-gpt5.html'

# Minimal manifest mirroring the browser's list
MANIFEST = [
    'system share/historical-entries/new-world-genesis-gpt5.md',
    'system share/historical-entries/terraformer-bootstrap-gpt5.md',
    'system share/historical-entries/neo-colonial-alliance-gpt5.md',
    'system share/historical-entries/great-fork-gpt5.md',
    'system share/historical-entries/new-world-genesis.md',
    'system share/historical-entries/terraformer-bootstrap.md',
    'system share/historical-entries/neo-colonial-alliance.md',
    'system share/historical-entries/great-fork.md',
    'system share/historical-entries/boostrap-encyclopedia-new-world-genesis-seeds-recipe.txt',
]

# Extend with core foundations (you can expand this list as needed)
FOUNDATION_DIRS = [
    PUBLIC / 'foundations',
    PUBLIC / 'dialectic-oracleness',
]

def discover_files():
    paths = list(MANIFEST)
    for base in FOUNDATION_DIRS:
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if p.suffix.lower() in ('.md', '.txt'):
                rel = str(p.relative_to(ROOT))
                rel = rel.replace('\\', '/')
                paths.append(rel)
    # De-duplicate preserving order
    seen = set()
    uniq = []
    for p in paths:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq

def read_text(path_str):
    p = ROOT / Path(path_str)
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''

def load_tours():
    tours = []
    if TOURS_DIR.exists():
        for p in TOURS_DIR.glob('*.json'):
            try:
                tours.append(json.loads(p.read_text(encoding='utf-8')))
            except Exception:
                pass
    return tours

def build_bundle(out_path=BUNDLE_OUT):
    files = []
    for path in discover_files():
        ext = Path(path).suffix.lower().lstrip('.')
        content = read_text(path) if ext in ('md','txt') else ''
        title = Path(path).name
        category = path.split('/')[-2] if '/' in path else 'root'
        files.append({
            'path': path,
            'title': title,
            'ext': ext,
            'category': category,
            'content': content,
        })
    # Build simple HTML using same static bundle template logic as browser
    data = json.dumps(files)
    tours_json = json.dumps(load_tours())
    html = fr"""<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>The New World Encyclopedia — Static Bundle (GPT-5)</title><style>
body{{margin:0;background:#0f172a;color:#e2e8f0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial}}
header{{padding:16px;border-bottom:1px solid #1f2937;background:#111827}}
h1{{margin:0;font-size:18px}}
.wrap{{display:grid;grid-template-columns:360px 1fr;height:calc(100vh - 66px)}}
.sidebar{{border-right:1px solid #1f2937;overflow:auto}}
.tools{{padding:10px;position:sticky;top:0;background:#0b1220;border-bottom:1px solid #1f2937}}
input,button{{background:#0b1220;color:#e2e8f0;border:1px solid #334155;padding:8px 10px;border-radius:6px;font-size:13px}}
button{{cursor:pointer}}
.item{{padding:10px;border:1px solid #1f2937;border-radius:8px;margin:8px;background:#0b1220;cursor:pointer}}
.viewer{{padding:16px;max-width:1200px;margin:0 auto}}
.viewer-content{{background:#0b1220;border:1px solid #1f2937;border-radius:10px;padding:16px;overflow:auto}}
mark{{background:#fde68a;color:#0f172a}}
</style></head><body>
<header><h1>Static Bundle — The New World Encyclopedia</h1></header>
<div class=\"wrap\"><aside class=\"sidebar\"><div class=\"tools\"><input id=\"q\" placeholder=\"Search...\"/></div><div id=\"list\"></div></aside><main><div class=\"viewer\"><div id=\"title\" class=\"heading\"></div><div id=\"meta\" class=\"meta\"></div><div id=\"view\" class=\"viewer-content\"></div></div></main></div>
<script>
const items = {data};
const tours = {tours_json};
function mdEscape(h){{return h.replace(/[&<>]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;"}}[c]))}}
function renderMarkdown(s){{if(!s)return"";let o=s.replace(/\r\n?/g,"\n");o=o.replace(/^\s*[-*+]\s*$/gm,'');o=o.replace(/```([\s\S]*?)```/g,(m,c)=>`<pre><code>${{mdEscape(c)}}</code></pre>`);o=o.replace(/`([^`]+)`/g,(m,c)=>`<code>${{mdEscape(c)}}</code>`);o=o.replace(/^######\s+(.+)$/gm,'<h6>$1</h6>').replace(/^#####\s+(.+)$/gm,'<h5>$1</h5>').replace(/^####\s+(.+)$/gm,'<h4>$1</h4>').replace(/^###\s+(.+)$/gm,'<h3>$1</h3>').replace(/^##\s+(.+)$/gm,'<h2>$1</h2>').replace(/^#\s+(.+)$/gm,'<h1>$1</h1>');o=o.replace(/^\s*---\s*$/gm,'<hr/>');o=o.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>').replace(/__([^_]+)__/g,'<strong>$1</strong>').replace(/_([^_]+)_/g,'<em>$1</em>');o=o.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1<\/a>');o=o.replace(/^(> .+(?:\n> .+)*)/gm,b=>{{const h=b.split(/\n/).map(l=>l.replace(/^>\s?/,'')).join('\n');return `<blockquote>${{h}}<\/blockquote>`}});o=o.replace(/^(\s*)([-*+]\s+.+)(?:\n\1[-*+]\s+.+)*$/gm,l=>{{const a=l.split(/\n/).map(x=>x.replace(/^\s*[-*+]\s+/,''));return '<ul>'+a.map(i=>`<li>${{i}}<\/li>`).join('')+'<\/ul>'}});o=o.replace(/^(\s*)(\d+\.\s+.+)(?:\n\1\d+\.\s+.+)*$/gm,l=>{{const a=l.split(/\n/).map(x=>x.replace(/^\s*\d+\.\s+/,''));return '<ol>'+a.map(i=>`<li>${{i}}<\/li>`).join('')+'<\/ol>'}});o=o.replace(/(^|\n)([^<\n][^\n]*)/g,(m,b,l)=>{{if(/^\s*(<h\d|<ul|<ol|<pre|<blockquote|<p|<hr|<table|<code)/.test(l))return m;if(l.trim()==='')return m;return `${{b}}<p>${{l}}<\/p>`}});return o}}
const q=document.getElementById('q'),list=document.getElementById('list'),view=document.getElementById('view'),title=document.getElementById('title'),meta=document.getElementById('meta');
q.addEventListener('input',renderList);
function filtered(){{const t=(q.value||'').toLowerCase();return items.filter(it=>!t||it.title.toLowerCase().includes(t)||it.path.toLowerCase().includes(t)||(it.content||'').toLowerCase().includes(t));}}
function renderList(){{list.innerHTML='';filtered().forEach(it=>{{const d=document.createElement('div');d.className='item';d.innerHTML=`<div class=title>${{it.title}}</div><div class=path>${{it.path}}</div>`;d.onclick=()=>open(it);list.appendChild(d)}})}}
function open(it){{title.textContent=it.title;meta.textContent=`${{it.path}}`;view.innerHTML=it.ext==='md'?renderMarkdown(it.content||''):`<pre>${{mdEscape(it.content||'')}}<\/pre>`}}
renderList();
</script></body></html>"""
    out_path.write_text(html, encoding='utf-8')
    print(f"Built static bundle: {out_path}")
    # Also write bundle to shared public folder
    try:
        BUNDLE_PUBLIC.write_text(html, encoding='utf-8')
        print(f"Built static bundle (public): {BUNDLE_PUBLIC}")
    except Exception as e:
        print(f"[WARN] Could not write public bundle: {e}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[HTTP]", fmt % args)

    def do_GET(self):
        # Quiet common noisy requests
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        if self.path == '/.well-known/appspecific/com.chrome.devtools.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'{}')
            return
        # Normalize duplicate "system share" path segments (encoded and decoded forms)
        p = self.path
        # Serve manifest.json dynamically
        if p == '/manifest.json':
            data = []
            try:
                for ext in ('.md', '.txt'):
                    for q in PUBLIC.rglob(f'*{ext}'):
                        rel = str(q.relative_to(ROOT)).replace('\\', '/')
                        title = q.name
                        category = q.parent.name
                        data.append({
                            'path': rel,
                            'title': title,
                            'ext': ext.lstrip('.'),
                            'category': category
                        })
            except Exception as e:
                pass
            body = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        # Encoded form
        while '/system%20share/system%20share/' in p:
            p = p.replace('/system%20share/system%20share/', '/system%20share/')
        # Decoded form
        while '/system share/system share/' in p:
            p = p.replace('/system share/system share/', '/system share/')
        if p != self.path:
            self.path = p
        return super().do_GET()

def serve(port=8000, watch=True):
    os.chdir(ROOT)
    build_bundle()
    def watcher():
        last = 0
        while watch:
            try:
                mtime = max((p.stat().st_mtime for p in PUBLIC.rglob('*') if p.is_file()), default=0)
                if mtime > last:
                    last = mtime
                    build_bundle()
            except Exception:
                pass
            time.sleep(2)
    if watch:
        threading.Thread(target=watcher, daemon=True).start()
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving on http://localhost:{port} (watching for changes)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down…")

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8000)
    ap.add_argument('--no-watch', action='store_true')
    args = ap.parse_args()
    serve(port=args.port, watch=not args.no_watch)
