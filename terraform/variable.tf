variable "project_id" {
  description = "GCP project ID"
  type        = string
  # No default — always supplied by CI/CD via secrets.GCP_PROJECT_ID
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "europe-west1-b"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  # Supplied by CI/CD via secrets.GKE_CLUSTER_NAME
}

variable "image_repo" {
  description = "Artifact Registry image repository path"
  type        = string
  # e.g. europe-west1-docker.pkg.dev/PROJECT_ID/app-images/secureapp
}

variable "image_tag" {
  description = "Container image tag to deploy (git SHA from CI)"
  type        = string
}

variable "database_url" {
  description = "SQLAlchemy DATABASE_URL injected into the app container"
  type        = string
  sensitive   = true
  # Format: mysql+pymysql://USER:PASS@/DB?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
  # Supplied by CI/CD via secrets.GCP_DB_URL — never committed to source control
}

variable "db_connection_name" {
  description = "Cloud SQL instance connection name for the sidecar proxy"
  type        = string
  # Format: project-id:region:instance-name
  # Supplied by CI/CD via secrets.GCP_DB_CONNECTION_NAME
}
