# Container recipe for the AskAnyDoc ingestion Lambda.
# It starts with AWS's Python 3.13 Lambda runtime, installs the extraction
# dependencies, and copies the ingestion handler into the Lambda task directory.

# Pin the current linux/amd64 image so repeated v1 builds use the same foundation.
FROM public.ecr.aws/lambda/python:3.13@sha256:719d661e93e438cf5c17d30e20328cac13c807a59a7935f73120f0e5835c3277

COPY requirements-cloud.lock requirements.txt
RUN pip install --no-deps -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

#Copy the application code into the image
#Copy the reusable RAG package and ingestion-specific adapters only.

COPY app/shared/askanydoc_rag "${LAMBDA_TASK_ROOT}/askanydoc_rag"
COPY app/ingestion/runtime/*.py "${LAMBDA_TASK_ROOT}/"

CMD ["ingestion_lambda_handler.handler"]
