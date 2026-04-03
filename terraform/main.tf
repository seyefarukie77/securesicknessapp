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

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = "app-images"
  format        = "DOCKER"
  description   = "App images"
}

data "google_client_config" "default" {}

resource "google_container_cluster" "gke" {
  name     = "my-gke-cluster"
  location = var.zone

  # Must match existing cluster
  deletion_protection = true

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
  name     = "default-pool"
  location = var.zone
  cluster  = google_container_cluster.gke.name

  node_count = 3

  node_config {
    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

#provider "kubernetes" {
#  host                   = google_container_cluster.gke.endpoint
#  token                  = data.google_client_config.default.access_token
#  cluster_ca_certificate = base64decode(google_container_cluster.gke.master_auth[0].cluster_ca_certificate)
#}

