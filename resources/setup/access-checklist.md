# Learning-account access checklist

Use this before the relevant service chapter. Keep completed identifiers in
local-records/environment-record.md. Do not put secret values in this checklist.

| Stage | Arrange with the account owner | Inspect before proceeding |
|---|---|---|
| Chapters 1-4 local work | Install approved local tools and extract the companion | Version commands and offline lab pass |
| Chapter 5 Entra | Work/school tenant; permission to create two registrations or an administrator who can do so | API scope, v2 token setting, separate browser ID and approved consent |
| Chapter 6 AWS | Learning account, billing owner, approved deployment role/profile | STS account and role match the agreed target |
| Chapter 6 AWS permissions | Owner reviews infra/ and supplies permissions for its named resources, IAM role creation/pass-role, model access and optional budgets | Registry and main plans contain only the learning resources |
| Chapter 9 SharePoint | Licensed learning users, two private sites, delegated Graph consent and API credential owner | Alex/Sam direct file access matches the matrix |
| Chapter 10 Salesforce | Org with API/Hosted MCP access, Setup administrator, ordinary test users and ECA permission-set owner | Read server active; known Case readable by the intended user |
| Chapter 12 retention | Owners for logs, queues, credentials, backups and cost | Retained/deleted resources recorded explicitly |

AWS, Microsoft and Salesforce accounts are separate. A software installation
does not grant cloud permissions or a subscription. Use the service owner's
approved learning environment rather than personal production credentials.
The required resources and actions are visible in infra/; do not apply an
unreviewed administrator policy merely to conceal a specific denied action.
