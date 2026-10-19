# Configuration templates

| Template | Local working copy | Used for |
|---|---|---|
| ../frontend/.env.example | frontend/.env.local | Public tenant, SPA, scope and API URL |
| ../infra/bootstrap/bootstrap.tfvars.example | infra/bootstrap/bootstrap.tfvars | Separate book ECR registry |
| ../infra/book.tfvars.example | infra/book.tfvars | Main book resources, model/digest and identity settings |
| ../resources/setup/environment-record.md | local-records/environment-record.md | Non-secret checkpoint/target record |
| ../resources/setup/access-checklist.md | Read before the service chapter | Account owners, access and direct checks |

Replace YOUR_ and REPLACE_ values using the account you own or are authorised
to use. Read identifiers from your Terraform outputs. Keep credential values
in the designated AWS Secrets Manager records; do not put them in Vite variables,
source or screenshots. Preserve one complete main variable file across plans
so enabling a new connector does not silently disable an earlier one.
