# Initial deployment checklist

Read Chapter 6 for explanations, exact commands and expected results. This
checklist is the same sequence, not a second architecture or an automatic script.

1. Install the prerequisites and run local checks from Chapters 1-5.
2. In the intended Entra tenant create the API and browser registrations, expose
   access_as_user, request v2 API access tokens and grant the browser permission.
3. Authenticate your approved AWS CLI profile. Verify account and Region with
   aws sts get-caller-identity. Record project prefix and cost owner privately.
4. Verify Titan embedding and the selected Converse/tool/JSON-capable answer
   model. Record profile ARN and destination model ARNs.
5. In infra/bootstrap copy bootstrap.tfvars.example to bootstrap.tfvars. Enter
   the new prefix/account/Region. Initialise, validate, save/review/apply the
   registry-only plan. Preserve its own state.
6. From the companion root build the ingestion image for Linux x86_64 with
   buildx --provenance=false --load. Check imports, authenticate to your ECR,
   push an immutable tag and read back the actual digest.
7. Run tools/build_packages.py --install and tools/verify_packages.py. Keep
   build folders generated; keep source changes in app/.
8. Fill infra/book.tfvars from the example. Use the same prefix/account/Region,
   the image digest and scoped model ARNs. Select an available compatible Aurora
   engine. Leave both enterprise connectors disabled initially.
9. Build frontend/dist. In infra initialise, format, validate and save a normal
   plan. Review only owned changes, private storage/database and JWT routes.
   Apply the exact approved plan and retain its outputs privately.
10. Add the new HTTPS origin as a browser SPA redirect in Entra. Update
    frontend/.env.local with your protected /chat URL. Rebuild, review/apply the
    asset changes and invalidate the CloudFront entry page. Test sign-in and
    rejection of an anonymous API request.
11. In Chapter 7 set the new database output identifiers and run tools/live.py
    schema, then database. In the same chapter upload the safe policy to the document
    bucket under uploads/. Inspect logs, rows, retrieval, answer and citation.
12. Enable SharePoint only after Chapter 9's site membership, delegated consent
    and credential steps. Preserve the same complete tfvars file on every plan.
13. Enable Salesforce only after Chapter 10's org, ECA and user setup. Keep the
    confidential web secret server-side and the learning connector serialised.
14. Run the integrated worksheet and record actual results. Keep paid resources
    only while owned and needed; use Chapter 12's reviewed cleanup sequence.

Terraform state, plan files and completed configuration stay private. The main
stack has its own two-AZ database network; no default VPC is required. The registry
bootstrap remains separately owned when the main stack is removed.
