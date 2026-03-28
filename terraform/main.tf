terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Artifact Registry (existing)
resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = "app-images"
  format        = "DOCKER"
}

# GKE Cluster (existing)
resource "google_container_cluster" "gke" {
  name     = "my-gke-cluster"
  location = var.zone

  remove_default_node_pool = false
  initial_node_count       = 1

  networking_mode = "VPC_NATIVE"

  ip_allocation_policy {}
}

# Node Pool (existing)
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
