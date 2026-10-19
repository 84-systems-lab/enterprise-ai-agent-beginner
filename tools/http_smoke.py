"""Exercise the real fixture HTTP boundary and stop only our own server process."""
from pathlib import Path
import json
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
with socket.socket() as reserve:
    reserve.bind(('127.0.0.1',0)); port=reserve.getsockname()[1]
flags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0
proc=subprocess.Popen([sys.executable,'-m','lab','serve','--port',str(port)],cwd=ROOT,
    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=flags)
try:
    url=f'http://127.0.0.1:{port}'
    for attempt in range(40):
        if proc.poll() is not None: raise RuntimeError('Our fixture server exited before readiness')
        try:
            page=urllib.request.urlopen(url,timeout=.4).read()
            assert b'Offline fixture lab' in page
            break
        except urllib.error.URLError: time.sleep(.1)
    else: raise TimeoutError('Our fixture server did not start')
    def post(body):
        request=urllib.request.Request(url+'/ask',data=json.dumps(body).encode(),
            headers={'Content-Type':'application/json'},method='POST')
        return urllib.request.urlopen(request,timeout=2)
    with post({'question':'damaged chair','sources':['aws'],'user':'alex'}) as response:
        payload=json.loads(response.read()); assert payload['citations'][0]['id']=='policy-returns'
    try:
        post({'question':''})
        raise AssertionError('Empty question was accepted')
    except urllib.error.HTTPError as error: assert error.code==400
    print(json.dumps({'http_get':200,'http_supported_question':200,'http_invalid_question':400,
                      'server_process_cleanup':'finally terminates only the process created here'}))
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait(timeout=5)
