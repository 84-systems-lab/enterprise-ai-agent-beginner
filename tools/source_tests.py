"""Run copied implementation tests with outbound networking disabled."""
from pathlib import Path
import os
import socket
import sys
import unittest
import faulthandler

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
os.environ.update(AWS_EC2_METADATA_DISABLED='true',AWS_ACCESS_KEY_ID='offline-test',
    AWS_SECRET_ACCESS_KEY='offline-test',AWS_DEFAULT_REGION='ap-southeast-2')
os.environ.pop('AWS_SESSION_TOKEN',None)
old_connect=socket.socket.connect
old_connect_ex=socket.socket.connect_ex
def local_only(sock,address):
    if isinstance(address,tuple) and address[0] in {'127.0.0.1','::1'}:
        return old_connect(sock,address)
    raise RuntimeError('External network disabled by offline test runner')
def local_only_ex(sock,address):
    if isinstance(address,tuple) and address[0] in {'127.0.0.1','::1'}:
        return old_connect_ex(sock,address)
    raise RuntimeError('External network disabled by offline test runner')
socket.socket.connect=local_only
socket.socket.connect_ex=local_only_ex
sys.path[:0]=[str(ROOT/'app'),str(ROOT/'app/api'),str(ROOT/'app/shared'),
             str(ROOT/'app/ingestion/runtime'),str(ROOT)]
group=sys.argv[1]
faulthandler.dump_traceback_later(30)
folders={'api':'app/api','ingestion':'app/ingestion/tests','salesforce':'app/salesforce'}
if group=='sharepoint':
    import pytest
    code=pytest.main(['-q','-p','no:cacheprovider',str(ROOT/'app/sharepoint/test_sharepoint_source.py')])
    faulthandler.cancel_dump_traceback_later()
    raise SystemExit(code)
if group not in folders: raise SystemExit('Use api, ingestion, salesforce or sharepoint.')
suite=unittest.TestLoader().discover(str(ROOT/folders[group]),pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
faulthandler.cancel_dump_traceback_later()
raise SystemExit(0 if result.wasSuccessful() else 1)
