import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .core import answer, inspect_document

parser = argparse.ArgumentParser(description='Offline fixture lab; no cloud calls')
parser.add_argument('command', choices=['ask', 'inspect', 'serve'])
parser.add_argument('value', nargs='?', default='What is the damaged chair policy?')
parser.add_argument('--sources', nargs='+', default=['aws'])
parser.add_argument('--user', choices=['alex', 'sam'], default='alex')
parser.add_argument('--port',type=int,default=8765)
args = parser.parse_args()

if args.command == 'ask':
    print(json.dumps(answer(args.value, args.sources, args.user), indent=2))
elif args.command == 'inspect':
    print(json.dumps(inspect_document(args.value), indent=2))
else:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/':
                self.send_error(404)
                return
            page = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Everyday Office Supplies evidence lab</title>
<style>body{font:18px system-ui;max-width:850px;margin:50px auto;padding:20px}
textarea{width:100%;min-height:80px}button,select{padding:10px;margin:12px 8px 12px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef3f5;padding:20px}</style>
<h1>Everyday Office Supplies</h1><p>Offline fixture lab. No live AI or enterprise access.</p>
<textarea id="q">What is the damaged chair policy?</textarea>
<select id="u"><option>alex</option><option>sam</option></select>
<button id="ask">Inspect evidence</button><pre id="result"></pre>
<script>document.querySelector('#ask').onclick=async()=>{
const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({question:document.querySelector('#q').value,
user:document.querySelector('#u').value,sources:['aws','sharepoint','salesforce']})});
document.querySelector('#result').textContent=JSON.stringify(await r.json(),null,2)};</script></html>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def do_POST(self):
            if self.path != '/ask':
                self.send_error(404)
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16000:
                    raise ValueError('Body must contain 1 to 16000 bytes')
                body = json.loads(self.rfile.read(length))
                result = answer(body['question'], body.get('sources', ['aws']), body.get('user', 'alex'))
                status = 200
            except (ValueError, TypeError, KeyError) as exc:
                result, status = {'error': str(exc)}, 400
            encoded = json.dumps(result).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_):
            pass  # avoid echoing user input into terminal logs

    if not 1024 <= args.port <= 65535: raise SystemExit('Use a port between 1024 and 65535')
    print(f'Offline fixture lab at http://127.0.0.1:{args.port}; Ctrl+C stops it.', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
