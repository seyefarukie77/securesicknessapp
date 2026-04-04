README — Secure Sickness Management Platform (Terraform + GKE + CI/CD)
Overview
# securesicknessapp
DevOps pipeline for Secure Sickness App
# Test pipeline
Trigger pipeline
trigger
This project implements a fully cloud‑native sickness management platform designed to support HR policy requirements such as:
- Recording sickness as a continuous period (including weekends)
- Notifying line managers on first day of sickness
- Handling threshold‑based requirements (e.g., fit notes)
- Securely storing uploaded documents (fit notes)
- Maintaining audit trails for submissions and approvals
- The platform is built using:
-   Python Web API (FastAPI/Flask) running in GKE
-   Cloud SQL (PostgreSQL) for sickness records and audit logs
-   Cloud Storage for fit note uploads
-   Secret Manager for secure credential injection
-   Artifact Registry for container images
-   Terraform for full infrastructure-as-code
-   GitHub Actions for CI/CD (build → push → terraform apply)

Folder structure (recommended)
Code
infra/
  main.tf
  providers.tf
  gke.tf
  artifact-registry.tf
  iam.tf
  kubernetes/
    deployment.tf
    service.tf
    namespace.tf
    variables.tf
Your application code stays in the repo root.

Architecture
1. Application Layer (Python API)
The backend provides:
- Employee sickness submission
- Manager approval workflow
- Fit note upload endpoint
- Audit logging
- Policy enforcement (thresholds, continuous periods)

The app runs inside a Docker container deployed to GKE.
Environment variables injected at runtime:
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD

FIT_NOTES_BUCKET
These are provisioned and managed by Terraform.

2. Infrastructure Layer (Terraform)
Terraform provisions and manages:
- GKE Cluster
    Regional cluster in europe-west1-b
    Node pool of e2-medium nodes
Kubernetes provider configured to apply manifests
Cloud SQL (PostgreSQL)
Instance: sickness-db
Database: sickness_app
User: sickness_user
Password stored in Secret Manager

Cloud Storage
Bucket for fit notes:
${project_id}-fit-notes

Secret Manager
Stores:

DB password

Optional: JWT secret, SMTP credentials, API keys

Artifact Registry
Repository:

Code
europe-west1-docker.pkg.dev/<project-id>/app-images/secureapp
Kubernetes Resources
Terraform manages:
- Deployment (secureapp)
- Service (secureapp-service)
- Secrets (db-credentials)
- Namespace (optional)

The Deployment image tag is controlled by Terraform via:
Code
-var="image_tag=<commit-sha>"

3. CI/CD Pipeline (GitHub Actions)
GitHub Actions performs:
Build
Build Docker image from the Python app
Tag image with commit SHA
Push
- Push image to Artifact Registry

Deploy
- Run terraform apply with the new image_tag

This triggers Terraform to update the Kubernetes Deployment, causing GKE to roll out the new version.

Workflow Summary
Code
push to main →
  GitHub Actions builds image →
  pushes to Artifact Registry →
  runs terraform apply →
  Terraform updates Deployment →
  GKE rolls out new pods
No manual kubectl commands are needed.

4. Directory Structure
Code
/
├── app/                     # Python API source code
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── infra/                   # Terraform infrastructure
│   ├── main.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── gke.tf
│   ├── artifact-registry.tf
│   ├── iam.tf
│   ├── sql.tf
│   ├── storage.tf
│   └── kubernetes/
│       ├── deployment.tf
│       ├── service.tf
│       ├── namespace.tf
│       └── variables.tf
│
└── .github/workflows/
    └── deploy.yaml          # CI/CD pipeline
5. Deployment Flow
Initial Setup
Clone repo

Configure Terraform backend 
Run:
Code
terraform init
terraform apply
Terraform creates:
- GKE cluster
- Cloud SQL
- Storage bucket
- Artifact Registry
- Secrets
- Kubernetes Deployment + Service
- Deploying New Code
- Developer pushes to main
- GitHub Actions:
-   Builds Docker image
-   Pushes to Artifact Registry
-   Runs terraform apply -var="image_tag=<sha>"
-   Terraform updates Deployment
-   GKE rolls out new pods

6. Database Schema (Conceptual)
employees
field	description
id	employee ID
name	employee name
email	employee email
line_manager_email	manager email
sickness_periods
field	description
id	sickness period ID
employee_id	FK to employees
start_date	first day
end_date	last day
status	PENDING / APPROVED / REJECTED
requires_fit_note	boolean
fit_note_url	GCS path
created_at	timestamp
updated_at	timestamp
sickness_events
Audit trail for all actions.

7. Observability
GKE automatically sends:
- Logs → Cloud Logging
- Metrics → Cloud Monitoring
- Events → Kubernetes API
- Optional Terraform resources can add:

8. Security
Secrets stored in Secret Manager
- DB password never appears in code or GitHub
- GKE nodes use private networking
- Fit notes stored in private GCS bucket
- IAM least privilege enforced via Terraform
- Service accounts used for CI/CD and GKE workloads

9. How to Run Locally
Code
- docker build -t secureapp .
- docker run -p 8000:8000 secureapp
- Environment variables must be set manually for local development.

10. Future Enhancements
Workload Identity (remove JSON keys entirely)
Horizontal Pod Autoscaler (HPA)
Ingress + HTTPS with Google-managed certificates
Pub/Sub notifications for manager alerts
Background jobs (Cloud Tasks or Cloud Run Jobs)
