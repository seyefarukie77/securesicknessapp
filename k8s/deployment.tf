resource "kubernetes_deployment" "secureapp" {
  metadata {
    name = "secureapp"
    labels = {
      app = "secureapp"
    }
  }

  spec {
    replicas = 2

    strategy {
      type = "RollingUpdate"

      rolling_update {
        max_surge       = 1
        max_unavailable = 0
      }
    }

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
          image = "${var.image_repo}:${var.image_tag}"

          port {
            container_port = 8000
          }
        }
      }
    }
  }
}