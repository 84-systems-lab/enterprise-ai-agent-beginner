"""Import each ZIP handler inside the target Lambda Linux runtime."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'public.ecr.aws/lambda/python:3.13@sha256:719d661e93e438cf5c17d30e20328cac13c807a59a7935f73120f0e5835c3277'

def main():
    for folder, module in [('build', 'answer_lambda_handler'),
                           ('answer_jobs_build', 'answer_job_worker'),
                           ('salesforce_web_build', 'salesforce.web_handler')]:
        path = (ROOT / 'infra' / folder).resolve()
        if not (path / 'boto3').exists():
            raise SystemExit('Run tools/build_packages.py --install before verifying.')
        subprocess.run(['docker', 'run', '--rm', '--platform', 'linux/amd64',
                        '--mount', f'type=bind,source={path},target=/var/task,readonly',
                        '-e', 'AWS_EC2_METADATA_DISABLED=true',
                        '-e', 'AWS_DEFAULT_REGION=ap-southeast-2',
                        '--entrypoint', '/var/lang/bin/python', IMAGE,
                        '-c', f'import importlib; importlib.import_module({module!r}); print({folder!r} + " imports OK")'], check=True)

if __name__ == '__main__':
    main()
