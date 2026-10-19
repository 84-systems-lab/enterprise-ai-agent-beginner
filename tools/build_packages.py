"""Build Python Lambda folders explicitly, before Terraform planning."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--install',action='store_true',help='Install pinned Linux dependencies')
args=parser.parse_args()
for name in ['build','answer_jobs_build','salesforce_web_build']:
    target=(ROOT/'infra'/name).resolve()
    if target.parent!=(ROOT/'infra').resolve(): raise ValueError('Unsafe build path')
    if target.exists(): shutil.rmtree(target)
    target.mkdir(exist_ok=True)
    if args.install:
        subprocess.run([sys.executable,'-m','pip','install','-r',str(ROOT/'requirements-cloud.lock'),
          '--target',str(target),'--platform','manylinux_2_34_x86_64','--platform','manylinux_2_28_x86_64',
          '--platform','manylinux2014_x86_64','--python-version','3.13',
          '--implementation','cp','--abi','cp313','--only-binary=:all:','--upgrade','--no-deps'],check=True)
    for path in (ROOT/'app/api').glob('*.py'):
        if not path.name.startswith('test_'): shutil.copy2(path,target/path.name)
    for source,dest in [('app/shared/askanydoc_rag','askanydoc_rag'),
                        ('app/sharepoint','sharepoint'),('app/salesforce','salesforce')]:
        out=target/dest; out.mkdir(exist_ok=True)
        for path in (ROOT/source).glob('*.py'):
            if not path.name.startswith('test_'): shutil.copy2(path,out/path.name)
    print(f'Prepared {name}; dependencies installed: {args.install}')
