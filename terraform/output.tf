output "cluster_name" {
  value = google_container_cluster.gke.name
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.app_images.repository_id
}
