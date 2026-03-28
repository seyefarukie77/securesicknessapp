resource "kubernetes_deployment" "secureapp" {
  metadata {
    name = "secureapp"
    labels = {
      app = "secureapp"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "secureapp"
      }
    }

    template {
      metadata {
        labels = {
          app = "secureapp"
        }
      }

      spec {
        container {
          name  = "secureapp"
          image = "europe-west1-docker.pkg.dev/${var.project_id}/app-images/secureapp:${var.image_tag}"

          port {
            container_port = 8000
          }
        }
      }
    }
  }
}
