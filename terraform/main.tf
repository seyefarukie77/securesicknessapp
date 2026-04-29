terraform {
  required_version = ">= 1.6.0"

  backend "gcs" {
    bucket = "securesicknessapp-tf-state"
    prefix = "securesicknessapp/terraform"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# ── GCP provider ────────────────────────────────────────────────────────────
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Used by the Kubernetes provider for short-lived auth tokens
data "google_client_config" "default" {}

# ── Artifact Registry ────────────────────────────────────────────────────────
resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = "app-images"
  format        = "DOCKER"
  description   = "Secure Sickness App container images"
}

# ── GKE cluster (import-only — lifecycle ignores all managed fields) ─────────
resource "google_container_cluster" "gke" {
  name     = var.cluster_name
  location = var.zone

  deletion_protection      = true
  remove_default_node_pool = false
  initial_node_count       = 0

  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {}
  network    = "default"
  subnetwork = "default"

  lifecycle {
    ignore_changes = [
      initial_node_count,
      remove_default_node_pool,
      node_pool,
      node_pool_defaults,
      node_config,
      node_pool_auto_config,
      addons_config,
      logging_config,
      monitoring_config,
      master_auth,
      release_channel,
      security_posture_config,
      private_cluster_config,
      workload_identity_config,
      cluster_autoscaling,
    ]
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "default-pool"
  location   = var.zone
  cluster    = google_container_cluster.gke.name
  node_count = 3

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

# ── Kubernetes provider — authenticated via GKE cluster outputs ──────────────
# This was commented out in your original file. It must be active for all
# kubernetes_* resources below to work. The pipeline runs
# gcloud container clusters get-credentials before terraform apply,
# which writes a kubeconfig entry. The provider reads that entry.
provider "kubernetes" {
  host  = "https://${google_container_cluster.gke.endpoint}"
  token = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.gke.master_auth[0].cluster_ca_certificate
  )
}

# ── Kubernetes Secret — DATABASE_URL never appears in plaintext in GKE ───────
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "secureapp-secrets"
    namespace = "default"
  }

  data = {
    DATABASE_URL       = var.database_url
    DB_CONNECTION_NAME = var.db_connection_name
  }
}

# ── Deployment ───────────────────────────────────────────────────────────────
resource "kubernetes_deployment" "secureapp" {
  metadata {
    name      = "secureapp"
    namespace = "default"
    labels    = { app = "secureapp" }
  }

  spec {
    replicas = 2

    selector {
      match_labels = { app = "secureapp" }
    }

    template {
      metadata {
        labels = { app = "secureapp" }
      }

      spec {
        # App container
        container {
          name  = "secureapp"
          image = "${var.image_repo}:${var.image_tag}"

          port {
            container_port = 8080
          }

          env {
            name = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }

          env {
            name  = "PORT"
            value = "8080"
          }

          env {
            name  = "PYTHONUNBUFFERED"
            value = "1"
          }

          # Readiness — GKE won't route traffic until /health returns 200
          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 10
            failure_threshold     = 3
          }

          # Liveness — GKE restarts the pod if /health stops responding
          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 15
            period_seconds        = 20
            failure_threshold     = 3
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "256Mi"
            }
          }
        }

        # Cloud SQL Auth Proxy sidecar — handles IAM-authenticated DB connections
        # This replaces the unix socket approach and requires no password in the URL
        container {
          name  = "cloud-sql-proxy"
          image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.11.0"

          args = [
            "--structured-logs",
            "--port=3306",
            "$(DB_CONNECTION_NAME)",
          ]

          env {
            name = "DB_CONNECTION_NAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "DB_CONNECTION_NAME"
              }
            }
          }

          security_context {
            run_as_non_root = true
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "200m"
              memory = "128Mi"
            }
          }
        }
      }
    }
  }

  # Force a rolling update whenever the image tag changes
  lifecycle {
    ignore_changes = []
  }
}

# ── Service — exposes the deployment via a GCP load balancer ─────────────────
resource "kubernetes_service" "secureapp" {
  metadata {
    name      = "secureapp"
    namespace = "default"
  }

  spec {
    selector = { app = "secureapp" }

    port {
      port        = 80
      target_port = 8080
      protocol    = "TCP"
    }

    type = "LoadBalancer"
  }
}

# ── Outputs — used by the monitor job to get SERVICE_URL ─────────────────────
output "load_balancer_ip" {
  description = "External IP of the LoadBalancer service — use as SERVICE_URL secret"
  value       = kubernetes_service.secureapp.status[0].load_balancer[0].ingress[0].ip
}

output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.gke.name
}
